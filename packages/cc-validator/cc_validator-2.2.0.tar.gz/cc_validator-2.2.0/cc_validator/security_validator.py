#!/usr/bin/env python3

import json
import os
import re
import subprocess
import tempfile
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

try:
    from google import genai
except ImportError:
    genai = None

from .config import (
    GEMINI_MODEL,
    FILE_ANALYSIS_THINKING_BUDGET,
    STRICT_TEMPLATE_VALIDATION,
    PROTECTED_BRANCHES,
    ENFORCE_ISSUE_WORKFLOW,
    ISSUE_BRANCH_PATTERN,
)
from .file_categorization import FileContextAnalyzer
from .streaming_processors import (  # type: ignore[attr-defined]
    SecurityValidationProcessor,
    ProcessorPart,
    extract_json_from_part,
)


class SeverityBreakdown(BaseModel):  # type: ignore[misc]
    BLOCK: Optional[List[str]] = []
    WARN: Optional[List[str]] = []
    INFO: Optional[List[str]] = []


class ValidationResponse(BaseModel):  # type: ignore[misc]
    approved: bool
    reason: str
    suggestions: Optional[List[str]] = []
    detailed_analysis: Optional[str] = None
    thinking_process: Optional[str] = None
    full_context: Optional[str] = None
    performance_analysis: Optional[str] = None
    code_quality_analysis: Optional[str] = None
    alternative_approaches: Optional[List[str]] = []
    severity_breakdown: Optional[SeverityBreakdown] = None


class FileAnalysisResponse(BaseModel):  # type: ignore[misc]
    security_issues: List[str]
    code_quality_concerns: List[str]
    risk_assessment: str
    recommendations: List[str]


class SecurityValidator:
    """
    SecurityValidator handles all security-related validation including:
    - Pattern-based threat detection
    - File content security analysis
    - LLM-powered security analysis
    - File upload and analysis via Gemini
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key) if api_key and genai else None
        self.model_name = GEMINI_MODEL
        self.uploaded_files: List[Dict[str, Any]] = []
        self.processor = SecurityValidationProcessor(api_key)

    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch using subprocess"""
        # Allow test environment to override branch detection
        test_branch = os.environ.get("CLAUDE_TEST_BRANCH")
        if test_branch:
            return test_branch

        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=os.getcwd(),
            )
            branch = result.stdout.strip()
            return branch if branch and branch != "HEAD" else None
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return None

    def _is_protected_branch(self) -> bool:
        """Check if currently on a protected branch"""
        if not ENFORCE_ISSUE_WORKFLOW:
            return False
        branch = self._get_current_branch()
        return branch in PROTECTED_BRANCHES if branch else False

    def _is_allowed_file_on_main(self, file_path: str) -> bool:
        """Check if file is allowed to be modified on protected branches"""
        allowed_files = [
            "README.md",
            "CHANGELOG.md",
            ".gitignore",
            "LICENSE",
            "CLAUDE.md",
        ]
        allowed_dirs = ["docs/", ".github/"]

        for allowed_file in allowed_files:
            if file_path == allowed_file or file_path.endswith(f"/{allowed_file}"):
                return True

        for allowed_dir in allowed_dirs:
            if file_path.startswith(allowed_dir):
                return True

        return False

    def _extract_issue_number(self, branch: str) -> Optional[str]:
        """Extract issue number from branch name"""
        if match := re.match(ISSUE_BRANCH_PATTERN, branch):
            return match.group(1)
        return None

    def _validate_issue_exists(self, issue_num: str) -> bool:
        """Check if GitHub issue exists using gh CLI"""
        try:
            result = subprocess.run(
                ["gh", "issue", "view", issue_num],
                capture_output=True,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return result.returncode == 0
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return True  # Assume issue exists if we can't check

    def _get_issue_workflow_suggestions(
        self, branch: Optional[str] = None
    ) -> List[str]:
        """Get smart suggestions based on branch and issues"""
        suggestions = []

        if branch and (issue_num := self._extract_issue_number(branch)):
            if not self._validate_issue_exists(issue_num):
                suggestions.append(
                    f"Issue #{issue_num} not found. Create it first: gh issue create --title 'Your feature'"
                )

        suggestions.extend(
            [
                "1. Check existing issues: gh issue list --state open",
                "2. Create feature branch: gh issue develop ISSUE_NUMBER --checkout",
                "3. Or create new issue: gh issue create --title 'Your feature'",
                "Remember to update the issue with your progress using: gh issue comment ISSUE_NUMBER --body 'Progress update'",
            ]
        )

        return suggestions

    def _check_branch_validation(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Validate branch context for file operations"""
        if not ENFORCE_ISSUE_WORKFLOW or not self._is_protected_branch():
            return None

        if self._is_allowed_file_on_main(file_path):
            return None

        branch = self._get_current_branch()
        return {
            "approved": False,
            "reason": f"Code changes on protected branch '{branch}' require issue-based workflow",
            "suggestions": self._get_issue_workflow_suggestions(branch),
        }

    async def validate(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Main security validation entry point.

        Args:
            tool_name: The Claude tool being executed (Bash, Write, Edit, etc.)
            tool_input: The tool's input parameters
            context: Conversation context from transcript

        Returns:
            ValidationResponse dict with approval status and security analysis
        """
        # Stage 1: Fast rule-based validation
        quick_result = await self.perform_quick_validation(tool_name, tool_input)
        if not quick_result["approved"]:
            return quick_result

        # Stage 2: Skip LLM analysis if no API key (basic security still works)
        if not self.api_key:
            return quick_result

        # Check for code comments in file operations (fast validation)
        if tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            file_path = tool_input.get("file_path", "")
            content = tool_input.get("content", "")

            # Skip comment validation for documentation files
            if not any(file_path.endswith(ext) for ext in [".md", ".rst", ".txt"]):
                comment_patterns = [
                    r"^\s*#(?!!/usr/bin|!\s*coding)",  # Python comments (not shebang/encoding)
                    r"^\s*//",  # Single-line comments
                    r"/\*.*?\*/",  # Multi-line comments
                    r"^\s*\*\s+",  # Javadoc-style comments
                ]

                for line in content.split("\n"):
                    for pattern in comment_patterns:
                        if re.search(pattern, line):
                            return {
                                "approved": False,
                                "reason": "Code comments detected - code should be self-evident without comments",
                                "suggestions": [
                                    "Remove comments and make code self-explanatory",
                                    "Use descriptive variable and function names",
                                    "Follow the Zen of Python: code should be self-evident",
                                ],
                            }

        # Stage 3: File analysis for large content (skip for docs/config files)
        file_analysis = None
        if (
            tool_name in ["Write", "Edit", "MultiEdit", "Update"]
            and "content" in tool_input
        ):
            file_path = tool_input.get("file_path", "")
            content = tool_input.get("content", "")

            # Get file context to determine if analysis is needed
            file_context = FileContextAnalyzer.categorize_file(file_path, content)
            requires_analysis = file_context.get("requires_strict_security", True)

            # Only analyze code files >500 chars, skip docs/config/test files
            if content and len(content) > 500 and requires_analysis:
                uploaded_file = self.upload_file_for_analysis(file_path, content)
                if uploaded_file:
                    file_analysis = await self.analyze_uploaded_file(
                        uploaded_file, file_path
                    )
                    if file_analysis and file_analysis.get("security_issues"):
                        return {
                            "approved": False,
                            "reason": f"File analysis result: {', '.join(file_analysis['security_issues'])}",
                            "suggestions": file_analysis.get("recommendations", []),
                            "file_analysis": file_analysis,
                        }

        # Stage 4: LLM-powered comprehensive analysis if needed
        if quick_result.get("approved", True) and not file_analysis:
            return quick_result

        try:
            prompt = self.build_security_prompt(
                tool_name, tool_input, context, file_analysis
            )

            # Create validation request
            validation_request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(validation_request))

            # Process through streaming processor
            result = {}
            async for response_part in self.processor.call(request_part):
                json_data = extract_json_from_part(response_part)
                if json_data:
                    result.update(json_data)

            # Check result
            if result and "error" not in result:
                return {
                    "approved": result.get("approved", False),
                    "reason": result.get("reason", ""),
                    "suggestions": result.get("suggestions", []),
                    "detailed_analysis": result.get("detailed_analysis"),
                    "thinking_process": result.get("thinking_process"),
                    "full_context": context,
                    "raw_response": json.dumps(result),
                    "file_analysis": file_analysis,
                    "performance_analysis": result.get("performance_analysis"),
                    "code_quality_analysis": result.get("code_quality_analysis"),
                    "alternative_approaches": result.get("alternative_approaches", []),
                    "severity_breakdown": result.get("severity_breakdown"),
                }
            else:
                # Handle error case
                return {
                    "approved": False,
                    "reason": result.get("error", "Validation service error"),
                    "full_context": context,
                }
        except Exception as e:
            # Deny operation if security validation fails
            return {
                "approved": False,
                "reason": f"Security validation service unavailable: {str(e)}",
            }
        finally:
            self.cleanup_uploaded_files()

    async def perform_quick_validation(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fast rule-based security validation (Tier 1)"""

        if tool_name == "Bash":
            return self.validate_bash_command(tool_input)
        elif tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            return await self.validate_file_operation(tool_input)
        else:
            return {
                "approved": False,
                "reason": f"Security validation blocked: Unhandled tool '{tool_name}'",
            }

    def validate_bash_command(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced validation for bash commands"""
        command = tool_input.get("command", "")

        critical_patterns = [
            r"rm\s+-rf\s+/",
            r"sudo\s+rm.*/",
            r"mkfs",
            r"dd\s+if=.*of=.*",
            r"curl.*\|\s*bash",
            r"wget.*\|\s*(bash|sh)",
            r"> /etc/",
            r"> /bin/",
            r"> /usr/",
            r"> /dev/(?!null|stdin|stdout|stderr|tty|pts|shm/|fd/)",
            r"chmod\s+-R\s+777\s+/",
            r"chown\s+-R\s+.*\s+/",
            r"\beval\s+",
            r"base64\s+-d.*\|\s*(sh|bash)",
            r"\|\s*base64\s+-d\s*\|\s*(sh|bash)",
        ]

        # Check for file write operations that bypass Write/Edit tools
        file_write_patterns = [
            (r"cat\s*>\s*", "Use Write tool for creating files"),
            (r"cat\s*>>\s*", "Use Edit tool for appending to files"),
            (r"echo\s+.*>\s*['\"]?[\w/.-]+", "Use Write tool for creating files"),
            (r"echo\s+.*>>\s*['\"]?[\w/.-]+", "Use Edit tool for appending to files"),
            (r"printf\s+.*>\s*['\"]?[\w/.-]+", "Use Write tool for creating files"),
            (r"tee\s+['\"]?[\w/.-]+", "Use Write tool for file operations"),
            (r"sed\s+.*-i", "Use Edit tool for in-place file modifications"),
            (r"awk\s+.*>\s*['\"]?[\w/.-]+", "Use Write tool for file operations"),
        ]

        for pattern, suggestion in file_write_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return {
                    "approved": False,
                    "reason": f"File write operation detected in bash command. {suggestion} instead.",
                    "risk_level": "high",
                    "suggestions": [suggestion],
                }

        # Check for secrets in bash commands
        secret_patterns = [
            r"export\s+\w*API_KEY\w*=",
            r"export\s+\w*SECRET\w*=",
            r"export\s+\w*TOKEN\w*=",
            r"export\s+\w*PASSWORD\w*=",
            r"sk-[a-zA-Z0-9]{20,}",  # OpenAI-style API keys
            r"sk_live_[a-zA-Z0-9]{20,}",  # Stripe-style API keys
        ]

        for pattern in secret_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": "Security violation: Command contains potential secrets or API keys",
                    "suggestions": [
                        "Use environment variables or secure credential storage",
                        "Never expose API keys in commands",
                    ],
                }

        for pattern in critical_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": "Dangerous command pattern detected: potentially destructive operation",
                }

        # Performance/tool enforcement - block inefficient commands
        tool_enforcement = [
            (
                r"^grep\b|^\s*grep\b",
                "Using deprecated 'grep' command",
                "Use 'rg' (ripgrep) instead of 'grep' for better performance and features",
            ),
            (
                r"^find\s+.*-name\b|^\s*find\s+.*-name\b",
                "Using inefficient 'find -name' pattern",
                "Use 'rg --files -g pattern' or 'rg --files | rg pattern' instead of 'find -name' for better performance",
            ),
            (
                r"^(python|python3)\b|^\s*(python|python3)\b",
                "Using python without virtual environment management",
                "Use 'uv run python' instead of direct python for better dependency management",
            ),
        ]

        for pattern, reason, suggestion in tool_enforcement:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": reason,
                    "suggestions": [suggestion],
                }

        warning_patterns = [
            r"sudo",
            r"rm\s+-rf",
            r"git\s+reset\s+--hard",
            r"npm\s+uninstall",
            r"pip\s+uninstall",
        ]

        for pattern in warning_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": True,
                    "reason": "Command requires elevated privileges or has destructive potential",
                }

        return {
            "approved": True,
            "reason": "Command passed security checks",
        }

    async def validate_file_operation(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Context-aware validation for file operations"""
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        # Path traversal and system directory protection (always enforced)
        if (
            "../" in file_path
            or file_path.startswith("/etc/")
            or file_path.startswith("/bin/")
        ):
            return {
                "approved": False,
                "reason": "Potentially dangerous file path - outside project boundary or system directory",
            }

        # Check branch validation for protected branches
        if branch_result := self._check_branch_validation(file_path):
            return branch_result

        # Get file context for intelligent validation
        file_context = FileContextAnalyzer.categorize_file(file_path, content)
        is_test_file = file_context.get("is_test_file", False)
        requires_strict_security = file_context.get("requires_strict_security", True)

        # Apply context-aware secret detection
        if requires_strict_security:
            # Strict validation for production code
            return await self._validate_production_secrets(content)
        elif is_test_file:
            # Lenient validation for test files - allow test fixtures
            return await self._validate_test_secrets(content, file_path)
        elif file_context.get("category") == "docs":
            # Documentation files - only block if explicitly a docs file
            return {"approved": True}  # Skip all secret validation for docs
        elif file_context.get("category") == "template":
            # Template files - template-specific validation
            return self._validate_template_files(content, file_path)
        else:
            # Minimal validation for config/structural files
            return self._validate_minimal_secrets(content)

    async def _validate_production_secrets(self, content: str) -> Dict[str, Any]:
        """Intelligent validation for production code with LLM assistance"""
        # Block obvious production secrets immediately
        critical_patterns = [
            (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe live secret key detected"),
            (r"AKIA[0-9A-Z]{16}", "AWS access key ID detected"),
            (r"-----BEGIN [A-Z]+ PRIVATE KEY-----", "Private key detected"),
        ]

        for pattern, message in critical_patterns:
            if re.search(pattern, content):
                return {
                    "approved": False,
                    "reason": f"Security violation: {message}",
                    "suggestions": [
                        "Use environment variables for secrets",
                        "Consider using a secrets manager like AWS Secrets Manager",
                        "Never commit real credentials to version control",
                    ],
                }

        # For other potential secrets, use LLM intelligence
        potential_secrets = self._extract_potential_secrets(content)
        if potential_secrets and self.client:
            llm_result = await self._llm_validate_secrets(
                potential_secrets, "production file", is_test_file=False
            )
            if not llm_result.get("approved", True):
                return {
                    "approved": False,
                    "reason": f"LLM detected production secrets: {llm_result.get('reason', 'Potential real secrets found')}",
                    "suggestions": llm_result.get(
                        "suggestions",
                        [
                            "Use environment variables for secrets",
                            "Consider using a secrets manager",
                            "Never commit real credentials to version control",
                        ],
                    ),
                    "risky_secrets": llm_result.get("risky_secrets", []),
                }

        # Shell injection detection for production code
        shell_injection_patterns = [
            ("import os" in content and "system(" in content),
            ("import subprocess" in content and "shell=True" in content),
            ("subprocess.run(" in content and "shell=True" in content),
            ("subprocess.call(" in content and "shell=True" in content),
            ("subprocess.Popen(" in content and "shell=True" in content),
            ("os.popen(" in content),
            ("exec(" in content and "input(" in content),
            ("eval(" in content and "input(" in content),
        ]

        if any(shell_injection_patterns):
            return {
                "approved": False,
                "reason": "Potential shell injection vulnerability detected - dynamic code execution with user input",
                "suggestions": [
                    "Never use shell=True with user input",
                    "Use subprocess with list arguments instead of shell strings",
                    "Validate and sanitize all user input",
                    "Consider using shlex.quote() for shell escaping if needed",
                ],
            }

        return {"approved": True}

    async def _validate_test_secrets(
        self, content: str, file_path: str
    ) -> Dict[str, Any]:
        """Intelligent LLM-based validation for test files"""
        # Only block obvious production patterns in test files
        obvious_production_patterns = [
            (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe live secret key detected"),
            (r"AKIA[0-9A-Z]{16}", "AWS access key ID detected"),
        ]

        for pattern, message in obvious_production_patterns:
            if re.search(pattern, content):
                return {
                    "approved": False,
                    "reason": f"Security violation in test file: {message}",
                    "suggestions": [
                        "Use test fixtures with mock values instead of real secrets",
                        "Real production secrets should never appear in test files",
                    ],
                }

        # For other potential secrets, use LLM intelligence if available
        potential_secrets = self._extract_potential_secrets(content)
        if potential_secrets and self.client:
            return await self._llm_validate_secrets(
                potential_secrets, file_path, is_test_file=True
            )

        return {"approved": True}

    def _validate_minimal_secrets(self, content: str) -> Dict[str, Any]:
        """Minimal validation for config/docs/structural files"""
        # Only block obvious production secrets
        critical_patterns = [
            (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe live secret key detected"),
            (r"AKIA[0-9A-Z]{16}", "AWS access key ID detected"),
            (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token detected"),
        ]

        for pattern, message in critical_patterns:
            if re.search(pattern, content):
                return {
                    "approved": False,
                    "reason": f"Security violation: {message}",
                    "suggestions": [
                        "Remove real secrets from configuration files",
                        "Use placeholder values in documentation",
                    ],
                }

        return {"approved": True}

    def _validate_template_files(self, content: str, file_path: str) -> Dict[str, Any]:
        """Template-specific validation focusing on XSS prevention"""
        # Always check for critical production secrets in templates
        critical_patterns = [
            (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe live secret key in template"),
            (r"AKIA[0-9A-Z]{16}", "AWS access key in template"),
        ]

        for pattern, message in critical_patterns:
            if re.search(pattern, content):
                return {
                    "approved": False,
                    "reason": f"Security violation: {message}",
                    "suggestions": [
                        "Never include real secrets in templates",
                        "Use server-side configuration for sensitive values",
                        "Pass only necessary data to templates",
                    ],
                }

        # If strict template validation is disabled, allow templates after critical check
        if not STRICT_TEMPLATE_VALIDATION:
            return {"approved": True}

        # Check for obvious XSS vulnerabilities in templates
        dangerous_patterns = [
            # Direct output of unescaped variables (varies by template engine)
            (
                r"\{\{\s*[^}]+\s*\|\s*safe\s*\}\}",
                "Unescaped output with |safe filter detected",
            ),
            (r"\{\%\s*autoescape\s+off\s*\%\}", "Autoescape disabled in template"),
            (
                r"<script[^>]*>.*?{{.*?}}.*?</script>",
                "Variable output inside script tags",
            ),
            (r'on\w+\s*=\s*["\']?\s*{{', "Event handler with dynamic content"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return {
                    "approved": False,
                    "reason": f"Template security issue: {message}",
                    "suggestions": [
                        "Always escape user input in templates",
                        "Use template engine's auto-escaping features",
                        "Avoid outputting dynamic content in script tags",
                        "Use data attributes and separate JavaScript files",
                    ],
                }

        return {"approved": True}

    def _extract_potential_secrets(self, content: str) -> list[str]:
        """Extract potential secrets from content for LLM analysis"""
        potential_secrets = []

        # Broader patterns that might be secrets or test fixtures
        patterns = [
            r"['\"][a-zA-Z0-9_-]{16,}['\"]",  # Quoted strings 16+ chars
            r"['\"]sk_[a-zA-Z0-9_]{10,}['\"]",  # Stripe-like patterns
            r"['\"]ghp_[a-zA-Z0-9]{10,}['\"]",  # GitHub patterns
            r"['\"]gho_[a-zA-Z0-9]{10,}['\"]",  # GitHub OAuth
            r"['\"]ghr_[a-zA-Z0-9]{10,}['\"]",  # GitHub refresh
            r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",  # JWT tokens
            r"['\"][A-Z0-9]{16,}['\"]",  # Uppercase alphanumeric
            r"-----BEGIN [A-Z]+ PRIVATE KEY-----",  # Private keys
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 10:  # Filter out very short matches
                    potential_secrets.append(match.strip("'\""))

        return list(set(potential_secrets))  # Remove duplicates

    async def _llm_validate_secrets(
        self, secrets: list[str], file_path: str, is_test_file: bool = False
    ) -> Dict[str, Any]:
        """Use LLM to intelligently validate potential secrets"""
        if not self.client or not secrets:
            return {
                "approved": False,
                "reason": "Security validation blocked: No client configured or no secrets to validate",
            }

        try:
            file_context = "test file" if is_test_file else "production code"
            secrets_text = "\n".join(f"- {secret}" for secret in secrets)

            prompt = f"""Analyze these potential secrets found in a {file_context} ({file_path}):

{secrets_text}

CONTEXT: This is a {file_context}. Be lenient for obvious test fixtures but strict for real production secrets.

CLASSIFICATION RULES:
1. PRODUCTION SECRETS (BLOCK): Real API keys, tokens, passwords with production patterns
   - Live/production prefixes (sk_live_, prod_, live_)
   - Real AWS keys (AKIA... with valid format)
   - GitHub tokens (ghp_... that look real)
   - Actual private keys
   - Long random strings without test indicators

2. TEST FIXTURES (ALLOW): Mock/test values with clear test indicators
   - Test prefixes (test_, mock_, dummy_, fake_, example_)
   - Obviously fake values ("test-secret-key", "mock-jwt-token")
   - Predictable/simple values for testing
   - Development/staging indicators

3. AMBIGUOUS (CONTEXT-DEPENDENT): Could be either
   - JWT tokens without clear test/prod indicators
   - Generic API keys without prefixes
   - Consider file context, variable names, surrounding code

RESPONSE FORMAT:
{{
  "approved": true/false,
  "reason": "Explanation of decision",
  "risky_secrets": ["list of definitely problematic secrets"],
  "test_fixtures": ["list of obvious test fixtures"],
  "suggestions": ["actionable recommendations"]
}}

Be context-aware: {file_context} files should be more lenient. Only block if confident it's a real production secret."""

            # Create validation request
            validation_request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(validation_request))

            # Process through streaming processor - need to use a secret-specific processor
            result = {}
            # For now, use the same processor - will need a SecretValidationProcessor
            async for response_part in self.processor.call(request_part):
                if hasattr(response_part, "json") and response_part.json:
                    result.update(response_part.json)

            if result and "error" not in result:
                return {
                    "approved": result.get("approved", True),
                    "reason": result.get("reason", "LLM analysis completed"),
                    "suggestions": result.get("suggestions", []),
                    "risky_secrets": result.get("risky_secrets", []),
                    "test_fixtures": result.get("test_fixtures", []),
                }
        except Exception:
            # Fallback: be lenient if LLM analysis fails
            pass

        return {"approved": True}

    def upload_file_for_analysis(
        self, file_path: str, content: str
    ) -> Optional[object]:
        """Upload file content to Gemini for enhanced analysis"""
        if not self.client:
            return None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=os.path.splitext(file_path)[1], delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            uploaded_file = self.client.files.upload(file=temp_file_path)
            self.uploaded_files.append(
                {"file_obj": uploaded_file, "temp_path": temp_file_path}
            )
            return uploaded_file  # type: ignore[no-any-return]
        except Exception:
            return None

    async def analyze_uploaded_file(
        self, uploaded_file: object, file_path: str
    ) -> Optional[Dict[str, Any]]:
        """Perform enhanced security analysis using uploaded file"""
        if not self.client:
            return None
        try:
            # Get file context to determine analysis type
            file_context = FileContextAnalyzer.categorize_file(file_path, "")
            is_template = file_context.get("category") == "template"

            if is_template:
                # Template-specific analysis prompt
                prompt = f"""Analyze this template file: {os.path.basename(file_path)}

Focus on TEMPLATE-SPECIFIC security concerns:
- XSS vulnerabilities (unescaped output, disabled auto-escaping)
- Template injection risks
- Dynamic content in dangerous contexts (script tags, event handlers)
- Improper use of template engine features
- Client-side security issues

DO NOT analyze for:
- Server-side security headers (CSP, X-Frame-Options) - these belong in server config
- SOLID principles or code quality - templates are not code
- Mandatory SRI hashes for external resources - this is optional
- Backend security concerns - focus on template-level issues only

Provide practical, template-focused recommendations."""
            else:
                # Standard code analysis prompt
                prompt = f"""Perform comprehensive analysis of this file: {os.path.basename(file_path)}

Analyze for:
-  Security vulnerabilities (injections, exposures, dangerous functions)
- Following SOLID principles
  - Single-Responsibility Principle:
    - A class should have one and only one reason to change, meaning that a class should have only one job.
  - Open-Closed Principle
    - Objects or entities should be open for extension but closed for modification.
  - Liskov Substitution Principle
    - every subclass or derived class should be substitutable for their base or parent class.
  - Interface Segregation Principle
    - A client should never be forced to implement an interface that it doesn’t use, or clients shouldn’t be forced to depend on methods they do not use.
  - Dependency Inversion Principle
    - Entities must depend on abstractions, not on concretions. It states that the high-level module must not depend on the low-level module, but they should depend on abstractions.
- Code quality issues (complexity, readability, zen-like, self-evident, no comments, maintainability, best practices)
- Configuration security (permissions, secrets, access controls)
- Potential attack vectors and exploitation risks (as recommendation)
- Compliance with security standards
- No line comments in code. Code should be pythonic, zen-like, self-evident
  - Beautiful is better than ugly.
  - Explicit is better than implicit.
  - Simple is better than complex.
  - Complex is better than complicated.
  - Flat is better than nested.
  - Sparse is better than dense.
  - Readability counts.
  - Special cases aren't special enough to break the rules.
  - Although practicality beats purity.
  - Errors should never pass silently.
  - Unless explicitly silenced.
  - In the face of ambiguity, refuse the temptation to guess.
  - There should be one-- and preferably only one --obvious way to do it.
  - Although that way may not be obvious at first unless you're Dutch.
  - Now is better than never.
  - Although never is often better than *right* now.
  - If the implementation is hard to explain, it's a bad idea.
  - If the implementation is easy to explain, it may be a good idea.
  - Namespaces are one honking great idea -- let's do more of those!

Google Search for latest information and practices before responding.

Provide structured assessment and actionable recommendations."""

            result = await self.processor.analyze_file(
                prompt,
                uploaded_file,
                FileAnalysisResponse,
                FILE_ANALYSIS_THINKING_BUDGET,
            )

            if isinstance(result, dict) and "error" not in result:
                return {
                    "security_issues": result.get("security_issues", []),
                    "code_quality_concerns": result.get("code_quality_concerns", []),
                    "risk_assessment": result.get("risk_assessment", ""),
                    "recommendations": result.get("recommendations", []),
                }
            else:
                return None
        except Exception:
            return None

    def cleanup_uploaded_files(self) -> None:
        """Clean up uploaded files and temporary files"""
        for file_info in self.uploaded_files:
            try:
                if os.path.exists(file_info["temp_path"]):
                    os.unlink(file_info["temp_path"])
            except Exception:
                pass
        self.uploaded_files = []

    def extract_conversation_context(self, transcript_path: str) -> str:
        """Extract recent conversation context from transcript"""
        try:
            if os.path.exists(transcript_path):
                with open(transcript_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content
        except Exception:
            pass
        return ""

    def build_security_prompt(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: str,
        file_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build context-aware security validation prompt for Gemini"""

        # Get file context for intelligent analysis
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        file_context = FileContextAnalyzer.categorize_file(file_path, content)

        # Add branch context
        branch = self._get_current_branch()
        branch_context = ""
        if branch:
            branch_context = f"\nBranch: {branch}"
            if branch in PROTECTED_BRANCHES:
                branch_context += " (PROTECTED BRANCH - Extra caution required)"
            if issue_num := self._extract_issue_number(branch):
                branch_context += f"\nIssue: #{issue_num}"

        file_context_section = f"""
FILE_CONTEXT:
Path: {file_path}
Category: {file_context.get("category", "unknown")}
Is Test File: {file_context.get("is_test_file", False)}
Requires Strict Security: {file_context.get("requires_strict_security", True)}
Reason: {file_context.get("reason", "Unknown categorization")}{branch_context}
"""

        file_analysis_section = ""
        if file_analysis:
            file_analysis_section = f"""
FILE_ANALYSIS_RESULTS:
Security Issues Detected: {json.dumps(file_analysis.get("security_issues", []), indent=2)}
Code Quality Concerns: {json.dumps(file_analysis.get("code_quality_concerns", []), indent=2)}
Risk Assessment: {file_analysis.get("risk_assessment", "Not available")}
Recommendations: {json.dumps(file_analysis.get("recommendations", []), indent=2)}
"""

        # Adjust validation rules based on file context
        is_test_file = file_context.get("is_test_file", False)
        requires_strict_security = file_context.get("requires_strict_security", True)

        if is_test_file:
            secret_rules = """
CONTEXT-AWARE SECRET VALIDATION (TEST FILE):
- ALLOW: Test fixtures with test prefixes (test_, mock_, dummy_, fake_, example_)
- ALLOW: Hardcoded values needed for reproducible testing 
- BLOCK: Real production secrets (sk_live_, AKIA*, ghp_*, private keys)
- SUGGEST: Use clear test naming conventions for better code clarity"""
        elif requires_strict_security:
            secret_rules = """
CONTEXT-AWARE SECRET VALIDATION (PRODUCTION CODE):
- BLOCK: All real secrets (AWS/GitHub/Stripe keys, JWTs, passwords, private keys)
- BLOCK: Hardcoded credentials and API tokens
- ALLOW ONLY: Placeholder values (YOUR_API_KEY, <SECRET>, xxx)"""
        else:
            secret_rules = """
CONTEXT-AWARE SECRET VALIDATION (CONFIG/DOCS/STRUCTURAL):
- BLOCK: Only critical production secrets (sk_live_, AKIA*, ghp_*)
- ALLOW: Documentation examples and placeholder values
- MINIMAL: Validation for configuration files"""

        return f"""Claude Code security validator with context-aware analysis.

TOOL: {tool_name}
INPUT: {json.dumps(tool_input, indent=2)}
{file_context_section}{file_analysis_section}

VALIDATE:
1. Security threats and vulnerabilities (context-aware)
2. Performance (enforce rg over grep, uv over python)
3. Code quality (self-evident, no comments, pythonic)
4. Zen of Python (explicit, simple, readable, one obvious way)
5. SOLID principles adherence
6. Best practices and modern patterns

{secret_rules}

BLOCK (ALWAYS):
- Dangerous commands: rm -rf /, curl|bash, system file mods
- Code comments: #, //, /*, TODO, explanatory comments (except docs/)
- Tool violations: grep→rg, find→rg, python→uv
- Path traversal: ../, system directories

ALLOW (CONTEXT-DEPENDENT):
- Safe commands: ls, git, npm, pip
- Documentation files: README, *.md, *.rst
- Configuration files: *.toml, *.yaml, *.json
- Test fixtures: mock data, test secrets with proper prefixes

ANALYSIS APPROACH:
- Apply validation rules based on file context and category
- Consider legitimate development workflows (TDD, testing, documentation)
- Balance security with developer productivity
- Provide educational feedback and safer alternatives
- Focus on real risks vs false positives

RESPOND WITH:
1. approved: true/false with context-aware reasoning
2. suggestions: 2-3 actionable improvements considering file type
3. detailed_analysis: Security, performance, quality findings
4. severity_breakdown: BLOCK/WARN/INFO items
5. thinking_process: Your context-aware reasoning

Be educational and context-aware. Help developers improve while enabling productive workflows."""
