#!/usr/bin/env python3
"""
100% Native genai-processors implementation.
Uses only @processor.part_processor_function decorators and native patterns.
No custom base classes - achieving 100% processor purity.
"""

import ast
import json
import os
import re
import subprocess
from typing import AsyncIterable, Optional, Dict, Any

try:
    from genai_processors import processor, content_api, streams
    from genai_processors.core import genai_model
    from google.genai import types
except ImportError:
    processor = None
    content_api = None
    streams = None
    genai_model = None
    types = None

from .file_storage import FileStorage
from .validation_dataclasses import (
    ToolInputData,
    ValidationResponse as CanonicalValidationResponse,
    FinalValidationResultData,
    create_part_from_dataclass,
    extract_tool_input_data,
)


def _extract_tool_input_data_safe(
    part: content_api.ProcessorPart,
) -> Optional[ToolInputData]:
    """Extract tool input data using canonical patterns with fallback logic"""
    # First try the canonical dataclass method
    tool_input_data = extract_tool_input_data(part)
    if tool_input_data:
        return tool_input_data

    # Fallback: handle raw JSON input manually
    try:
        if hasattr(part, "text") and part.text:
            data = json.loads(part.text)
        elif hasattr(part, "json") and part.json:
            data = dict(part.json)
        else:
            return None

        # Check if we have the required fields for ToolInputData
        if "tool_name" in data and "tool_input" in data:
            return ToolInputData(
                tool_name=data["tool_name"],
                tool_input=data["tool_input"],
                context=data.get("context", ""),
                api_key=data.get("api_key"),
                pipeline_initialized=data.get("pipeline_initialized", False),
                storage_context=data.get("storage_context", {}),
            )
        return None
    except (json.JSONDecodeError, AttributeError, TypeError, KeyError):
        return None


def count_test_functions(code_content: str) -> int:
    """Count test functions in Python code using AST parsing with regex fallback."""
    if not code_content:
        return 0

    try:
        tree = ast.parse(code_content)
        test_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_count += 1

        return test_count
    except SyntaxError:
        return len(re.findall(r"^def test_\w+\s*\(", code_content, re.MULTILINE))


# Branch validation flag - can be disabled for testing
ENFORCE_ISSUE_WORKFLOW = True


class BranchValidationPureFunctions:
    """Pure functions for Git branch and GitHub issue workflow validation."""

    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get the current git branch name."""
        test_branch = os.environ.get("CLAUDE_TEST_BRANCH")
        if test_branch:
            return test_branch if test_branch != "" else None

        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=os.getcwd(),
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                if branch == "HEAD":
                    return None
                return branch
        except Exception:
            pass
        return None

    @staticmethod
    def is_protected_branch(branch_name: Optional[str] = None) -> bool:
        """Check if a branch is protected (main/master)."""
        if branch_name is None:
            branch_name = BranchValidationPureFunctions.get_current_branch()
        if not branch_name:
            return False
        protected_branches = ["main", "master"]
        return branch_name in protected_branches

    @staticmethod
    def is_allowed_file_on_main(file_path: str) -> bool:
        """Check if a file is allowed to be modified on main branch."""
        allowed_files = [
            "README.md",
            "CLAUDE.md",
            "GEMINI.md",
            ".github/workflows/",
            "docs/",
        ]
        file_name = os.path.basename(file_path)
        for allowed in allowed_files:
            if file_name == allowed or file_path.startswith(allowed):
                return True
        return False

    @staticmethod
    def extract_issue_number(branch_name: str) -> Optional[str]:
        """Extract issue number from branch name (e.g., '123-feature' -> '123')."""
        if not branch_name:
            return None
        match = re.match(r"^(\d+)-", branch_name)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def validate_issue_exists(issue_number: str) -> bool:
        """Check if a GitHub issue exists."""
        try:
            result = subprocess.run(
                ["gh", "issue", "view", issue_number],
                capture_output=True,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return True
        except Exception:
            return False

    @staticmethod
    def get_issue_workflow_suggestions(branch_name: str) -> list:
        """Get issue workflow suggestions for a branch name."""
        issue_number = BranchValidationPureFunctions.extract_issue_number(branch_name)

        if issue_number and not BranchValidationPureFunctions.validate_issue_exists(
            issue_number
        ):
            return [
                f"Issue #{issue_number} not found",
                "Or check existing issues with: gh issue list",
                "Create the issue with: gh issue create",
            ]

        return [
            "Use feature branches for development",
            "Create issues before implementing features",
            "Follow branch naming convention: 123-feature-description",
        ]

    @staticmethod
    def validate_branch_workflow(file_path: str) -> Optional[Dict[str, Any]]:
        """Pure function for branch workflow validation."""
        if not ENFORCE_ISSUE_WORKFLOW:
            return None

        current_branch = BranchValidationPureFunctions.get_current_branch()

        if current_branch is None:
            return None

        if BranchValidationPureFunctions.is_protected_branch(current_branch):
            if BranchValidationPureFunctions.is_allowed_file_on_main(file_path):
                return None
            else:
                return {
                    "approved": False,
                    "reason": f"Direct modifications to protected branch '{current_branch}' are not allowed",
                    "suggestions": [
                        "Create a feature branch for your changes",
                        "Use pull requests to merge changes to main",
                    ],
                }

        issue_number = BranchValidationPureFunctions.extract_issue_number(
            current_branch
        )
        if issue_number and not BranchValidationPureFunctions.validate_issue_exists(
            issue_number
        ):
            return {
                "approved": False,
                "reason": f"Branch references non-existent issue #{issue_number}",
                "suggestions": [
                    f"Create issue #{issue_number} before continuing",
                    "Use existing issue numbers for branch names",
                ],
            }

        return None


def validate_security_pure(
    tool_name: str, tool_input: Dict[str, Any]
) -> Dict[str, Any]:
    """Pure function for security validation - no side effects or state dependencies."""
    return SecurityValidationPureFunctions.validate_tool_operation(
        tool_name, tool_input
    )


def validate_tdd_pure(
    tool_name: str, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Pure function for TDD validation - no side effects or state dependencies."""
    return TDDValidationPureFunctions.validate_tool_operation(
        tool_name, tool_input, tdd_context
    )


class SecurityValidationPureFunctions:
    """Pure functions for security validation - stateless and side-effect free."""

    @staticmethod
    def validate_tool_operation(
        tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main security validation entry point - pure function with threat detection."""

        # Enhanced threat detection patterns
        threat_patterns = {
            "sql_injection": [
                "'; DROP TABLE",
                "OR 1=1",
                "UNION SELECT",
                "'; --",
                "1=1--",
            ],
            "xss": ["<script>", "javascript:", "onerror=", "onclick=", "<iframe"],
            "path_traversal": ["../", "..\\", "%2e%2e", "..%2f", "..%5c"],
            "command_injection": ["; rm -rf", "| nc", "$(", "`", "&&", "||"],
            "aws_secret": ["AKIA", "sk_live_", "sk_test_"],
            "stripe_secret": ["sk_live_", "sk_test_", "rk_live_", "rk_test_"],
        }

        # Check for threat patterns in tool input
        input_str = json.dumps(tool_input).lower()
        threats_detected = []
        for threat_type, patterns in threat_patterns.items():
            for pattern in patterns:
                if pattern.lower() in input_str:
                    threats_detected.append(threat_type)
                    break

        # If threats detected, return early with critical severity
        if threats_detected:
            # Generate specific reason messages for secrets
            reasons = []
            for threat in threats_detected:
                if threat == "aws_secret":
                    reasons.append("AWS Access secret key detected")
                elif threat == "stripe_secret":
                    reasons.append("Stripe API secret key detected")
                else:
                    reasons.append(f"{threat} detected")

            reason = (
                "; ".join(reasons)
                if len(reasons) > 1
                else (
                    reasons[0]
                    if reasons
                    else f"Security threats detected: {', '.join(threats_detected)}"
                )
            )

            return {
                "approved": False,
                "reason": reason,
                "severity": (
                    "critical"
                    if any(
                        t
                        in [
                            "command_injection",
                            "sql_injection",
                            "aws_secret",
                            "stripe_secret",
                        ]
                        for t in threats_detected
                    )
                    else "high"
                ),
                "threats_detected": threats_detected,
                "suggestions": [
                    "Remove or escape dangerous patterns",
                    "Validate and sanitize all inputs",
                    "Use parameterized queries for database operations",
                    "Apply proper output encoding for web content",
                ],
            }

        # Tool routing validation
        allowed_tools = {"Write", "Edit", "Bash", "MultiEdit", "Update", "TodoWrite"}
        if tool_name not in allowed_tools:
            return {
                "approved": False,
                "reason": f"Unhandled tool: {tool_name}",
                "severity": "critical",
                "suggestions": [
                    f"Use one of the allowed tools: {', '.join(allowed_tools)}"
                ],
            }

        # Bash command validation
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            return SecurityValidationPureFunctions.validate_bash_command(command)

        # File operation security validation
        if tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            file_path = tool_input.get("file_path", "")
            content = SecurityValidationPureFunctions.extract_content_from_tool_input(
                tool_name, tool_input, file_path
            )
            return SecurityValidationPureFunctions.validate_file_content(
                content, file_path
            )

        # Default case - approve
        return {
            "approved": True,
            "reason": "Security validation passed",
            "severity": "none",
            "suggestions": [],
        }

    @staticmethod
    def validate_bash_command(command: str) -> Dict[str, Any]:
        """Pure function for bash command validation."""

        # Critical destructive patterns
        critical_patterns = [
            r"rm\s+-rf\s+/",
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

        for pattern in critical_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": "Dangerous command pattern detected: potentially destructive operation",
                    "severity": "critical",
                    "suggestions": [
                        "Review command for security implications",
                        "Use safer alternatives",
                    ],
                }

        # Tool enforcement patterns
        tool_enforcement = [
            (r"grep\s", "rg", "Using 'grep' command - use 'rg' instead"),
            (
                r"find\s.*-name",
                "rg",
                "Using inefficient 'find -name' pattern - use 'rg' instead",
            ),
        ]

        for pattern, replacement, reason in tool_enforcement:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": reason,
                    "severity": "medium",
                    "suggestions": [f"Use '{replacement}' instead"],
                }

        # File write detection
        file_write_patterns = [
            r"cat\s*>\s*",
            r"cat\s*>>\s*",
            r"echo\s+.*>\s*['\"]?[\w/.-]+",
            r"echo\s+.*>>\s*['\"]?[\w/.-]+",
            r"tee\s+['\"]?[\w/.-]+",
            r"sed\s+.*-i",
        ]

        for pattern in file_write_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "approved": False,
                    "reason": "File write operation detected in bash command. Use Write/Edit tools instead.",
                    "severity": "high",
                    "suggestions": [
                        "Use Write tool for creating files",
                        "Use Edit tool for modifying files",
                    ],
                }

        return {
            "approved": True,
            "reason": "Bash command security validation passed",
            "severity": "none",
            "suggestions": [],
        }

    @staticmethod
    def validate_file_content(content: str, file_path: str) -> Dict[str, Any]:
        """Pure function for file content security validation."""

        # Check if this is a test file - be more lenient with test fixtures
        is_test_file = SecurityValidationPureFunctions.is_test_file(file_path)

        # Secret detection patterns - skip for test files with mock data
        if not is_test_file:
            secret_result = SecurityValidationPureFunctions.detect_secrets(content)
            if not secret_result["approved"]:
                return secret_result

        # Comment detection (based on user instructions)
        if not SecurityValidationPureFunctions.should_skip_comment_validation(
            file_path, is_test_file
        ):
            comment_result = SecurityValidationPureFunctions.detect_comments(content)
            if not comment_result["approved"]:
                return comment_result

        # Template security for HTML/Jinja2 files (in addition to general checks above)
        if file_path.endswith((".html", ".htm", ".jinja2", ".j2")):
            template_result = (
                SecurityValidationPureFunctions.validate_template_security(content)
            )
            if not template_result["approved"]:
                return template_result

        return {
            "approved": True,
            "reason": "File content security validation passed",
            "severity": "none",
            "suggestions": [],
        }

    @staticmethod
    def is_test_file(file_path: str) -> bool:
        """Pure function to determine if a file is a test file."""
        filename = os.path.basename(file_path)

        # Standard test file patterns
        if (
            file_path.endswith("_test.py")
            or file_path.endswith("_spec.py")
            or file_path.endswith(".test.py")
            or file_path.endswith(".spec.py")
            or file_path.endswith(".spec.js")
            or file_path.endswith(".spec.ts")
            or file_path.endswith(".test.js")
            or file_path.endswith(".test.ts")
        ):
            return True

        # Files in test directories
        if (
            "/tests/" in file_path
            or "/test/" in file_path
            or "/spec/" in file_path
            or "/__tests__/" in file_path
        ):
            return True

        # Special case: files starting with test_
        # These are likely test files if they follow test naming conventions
        # e.g., test_feature.py, test_validation.py, test_module.py
        # But NOT test_data.py, test_config.py, test_impl.py (these are likely implementation)
        if filename.startswith("test_") and file_path.endswith(".py"):
            # Common implementation file patterns that start with test_
            impl_patterns = [
                "test_data",
                "test_config",
                "test_impl",
                "test_helper",
                "test_util",
            ]
            base_name = filename[:-3]  # Remove .py

            # If it matches common implementation patterns, it's not a test
            if any(base_name == pattern for pattern in impl_patterns):
                return False

            # If it's in a test directory, definitely a test
            if "/tests/" in file_path or "/test/" in file_path:
                return True

            # Otherwise, assume it's a test file (common pattern for test files)
            # This handles cases like test_simple_validation.py
            return True

        return False

    @staticmethod
    def detect_secrets(content: str) -> Dict[str, Any]:
        """Pure function for secret detection."""
        secret_patterns = [
            (r"sk-[a-zA-Z0-9_]{32,}", "OpenAI API secret key detected"),
            (r"sk_(live|test)_[a-zA-Z0-9_]{24,}", "Stripe API secret key detected"),
            (r"AKIA[0-9A-Z]{16}", "AWS Access secret key detected"),
            (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access secret token detected"),
            (
                r"['\"]?[A-Z_]*KEY['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                "Generic API secret key detected",
            ),
            (
                r"['\"]?[A-Z_]*SECRET['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                "Secret key detected",
            ),
            (
                r"['\"]?[A-Z_]*TOKEN['\"]?\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                "Secret token detected",
            ),
        ]

        for pattern, description in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    match_text = match.group(0).lower()
                else:
                    continue
                # Allow test/mock/fixture data
                if any(
                    test_word in match_text
                    for test_word in ["test", "mock", "fixture", "dummy", "fake"]
                ):
                    continue

                return {
                    "approved": False,
                    "reason": f"Security: {description}",
                    "severity": "critical",
                    "suggestions": [
                        "Remove sensitive data",
                        "Use environment variables or secure storage",
                    ],
                }

        return {"approved": True}

    @staticmethod
    def should_skip_comment_validation(file_path: str, is_test_file: bool) -> bool:
        """Pure function to determine if comment validation should be skipped."""
        return (
            file_path.endswith(
                (".html", ".htm", ".jinja2", ".j2", ".md", ".rst", ".txt")
            )
            or is_test_file
        )

    @staticmethod
    def detect_comments(content: str) -> Dict[str, Any]:
        """Pure function for comment detection."""
        # Hash comments (exclude URLs and HTML fragments)
        hash_comments = re.search(r"#.*\S", content)
        has_comments = False
        if hash_comments:
            comment_match = hash_comments.group(0)
            if not re.search(r"https?://|#[a-zA-Z0-9_-]+\s*$", comment_match):
                has_comments = True

        # Slash comments (exclude URLs)
        if not has_comments:
            slash_comments = re.search(r"//.*\S", content)
            if slash_comments:
                comment_start = content.find(slash_comments.group(0))
                preceding_text = content[max(0, comment_start - 10) : comment_start]
                if not re.search(r"https?$", preceding_text):
                    has_comments = True

        if has_comments:
            return {
                "approved": False,
                "reason": "Security: Code contains comments which are not allowed",
                "severity": "high",
                "suggestions": [
                    "Remove all comments from code",
                    "Code should be self-evident",
                ],
            }

        return {"approved": True}

    @staticmethod
    def validate_template_security(content: str) -> Dict[str, Any]:
        """Pure function for template security validation."""
        xss_patterns = [
            r"{{\s*[^|]*\s*\|\s*safe\s*}}",  # Jinja2 |safe filter (dangerous)
            r"<script[^>]*>.*?</script>",  # Script tags (potentially dangerous)
        ]

        for pattern in xss_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return {
                    "approved": False,
                    "reason": "Template Security: Potential XSS vulnerability - Unescaped output detected",
                    "severity": "critical",
                    "suggestions": [
                        "Escape all user output",
                        "Use |e or |escape filters in Jinja2",
                    ],
                }

        return {
            "approved": True,
            "reason": "Template security validation passed",
            "severity": "none",
            "suggestions": [],
        }

    @staticmethod
    def extract_content_from_tool_input(
        tool_name: str, tool_input: Dict[str, Any], file_path: str
    ) -> str:
        """Pure function to extract content from tool input."""
        if tool_name == "Write":
            return tool_input.get("content", "")  # type: ignore[no-any-return]
        elif tool_name == "Edit":
            return tool_input.get("new_string", "")  # type: ignore[no-any-return]
        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            content_parts = [edit.get("new_string", "") for edit in edits]
            return "\n".join(content_parts)
        elif tool_name == "Update":
            return tool_input.get("content", "")  # type: ignore[no-any-return]
        else:
            return ""


class TDDValidationPureFunctions:
    """Pure functions for TDD validation - stateless and side-effect free."""

    @staticmethod
    def validate_tool_operation(
        tool_name: str, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main TDD validation entry point - pure function with test framework detection."""

        # Check TDD relevance
        tdd_relevant_operations = ["Write", "Edit", "MultiEdit", "Update"]
        if tool_name not in tdd_relevant_operations:
            return {
                "approved": True,
                "reason": "TDD validation not applicable to this tool operation",
                "tdd_phase": "skipped",
                "suggestions": [],
            }

        # File categorization and validation
        file_path = tool_input.get("file_path", "")
        file_category = TDDValidationPureFunctions.categorize_file(file_path)

        # Detect test framework based on file extension
        test_frameworks = {
            ".py": "pytest",
            ".js": "jest",
            ".jsx": "jest",
            ".ts": "jest",
            ".tsx": "jest",
            ".go": "go test",
            ".rs": "cargo test",
            ".java": "junit",
            ".rb": "rspec",
            ".php": "phpunit",
            ".cs": "nunit",
            ".cpp": "gtest",
            ".c": "cunit",
        }

        # Get file extension and framework
        import os

        _, ext = os.path.splitext(file_path)
        test_framework = test_frameworks.get(ext, None)

        if file_category == "test":
            return TDDValidationPureFunctions.handle_test_file(
                tool_name, tool_input, file_path
            )
        elif file_category in ["structural", "docs", "config", "template"]:
            return {
                "approved": True,
                "reason": f"TDD validation not required for {file_category} files.",
                "tdd_phase": "skipped",
                "suggestions": [],
            }
        elif file_category == "implementation":
            return TDDValidationPureFunctions.handle_implementation_file(
                tdd_context, test_framework, file_path
            )
        else:
            return {
                "approved": True,
                "reason": "TDD validation not required for unknown file types.",
                "tdd_phase": "skipped",
                "suggestions": [],
            }

    @staticmethod
    def categorize_file(file_path: str) -> str:
        """Pure function for file categorization."""
        filename = os.path.basename(file_path)

        # Check if it's a test file using the same logic as is_test_file
        is_test = False

        # Standard test file patterns
        if (
            file_path.endswith("_test.py")
            or file_path.endswith("_spec.py")
            or file_path.endswith(".test.py")
            or file_path.endswith(".spec.py")
            or file_path.endswith(".spec.js")
            or file_path.endswith(".spec.ts")
            or file_path.endswith(".test.js")
            or file_path.endswith(".test.ts")
        ):
            is_test = True

        # Files in test directories
        elif (
            "/tests/" in file_path
            or "/test/" in file_path
            or "/spec/" in file_path
            or "/__tests__/" in file_path
        ):
            is_test = True

        # Special case: files starting with test_
        # These are likely test files if they follow test naming conventions
        elif filename.startswith("test_") and file_path.endswith(".py"):
            # Common implementation file patterns that start with test_
            impl_patterns = [
                "test_data",
                "test_config",
                "test_impl",
                "test_helper",
                "test_util",
            ]
            base_name = filename[:-3]  # Remove .py

            # If it matches common implementation patterns, it's not a test
            if any(base_name == pattern for pattern in impl_patterns):
                is_test = False
            else:
                # It's a test file (common pattern for test files)
                # Or it's in a test directory
                is_test = True

        if is_test:
            return "test"
        elif (
            file_path.endswith("__init__.py")
            or file_path.endswith("setup.py")
            or file_path.endswith("conftest.py")
        ):
            return "structural"
        elif file_path.endswith((".py", ".js", ".ts")):
            return "implementation"
        elif file_path.endswith((".md", ".rst", ".txt")) or "README" in filename:
            return "docs"
        elif file_path.endswith((".json", ".yaml", ".yml", ".toml", ".ini")):
            return "config"
        elif file_path.endswith(
            (
                ".html",
                ".htm",
                ".jinja2",
                ".j2",
                ".tpl",
                ".tmpl",
                ".hbs",
                ".handlebars",
                ".ejs",
                ".mustache",
                ".liquid",
                ".erb",
                ".twig",
                ".vue",
                ".svelte",
            )
        ) or any(
            part in file_path.lower()
            for part in ["templates", "views", "layouts", "partials", "components"]
        ):
            return "template"
        else:
            return "unknown"

    @staticmethod
    def handle_test_file(
        tool_name: str, tool_input: Dict[str, Any], file_path: str
    ) -> Dict[str, Any]:
        """Pure function for test file validation."""

        # Extract old and new content based on tool type
        old_content, new_content = TDDValidationPureFunctions.extract_test_contents(
            tool_name, tool_input, file_path
        )

        # Use the preserved analyze_test_changes function
        test_analysis = analyze_test_changes(
            old_content, new_content, file_path, tool_name
        )

        return {
            "approved": test_analysis["approved"],
            "reason": test_analysis["reason"],
            "tdd_phase": test_analysis["tdd_phase"],
            "suggestions": test_analysis["suggestions"],
            "test_count": test_analysis.get("test_count", 0),
        }

    @staticmethod
    def extract_test_contents(
        tool_name: str, tool_input: Dict[str, Any], file_path: str
    ) -> tuple[str, str]:
        """Pure function to extract old and new content for test analysis."""
        old_content = ""
        new_content = ""

        if tool_name == "Write":
            new_content = tool_input.get("content", "")
        elif tool_name == "Edit":
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                except Exception:
                    old_content = ""

            old_string = tool_input.get("old_string", "")
            new_string = tool_input.get("new_string", "")
            if old_string and old_string in old_content:
                new_content = old_content.replace(old_string, new_string, 1)
            elif not old_content and new_string:
                new_content = new_string
            else:
                new_content = old_content
        elif tool_name == "MultiEdit":
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                        new_content = old_content
                except Exception:
                    old_content = ""
                    new_content = ""
            else:
                old_content = ""
                new_content = ""

            edits = tool_input.get("edits", [])
            for edit in edits:
                old_string = edit.get("old_string", "")
                new_string = edit.get("new_string", "")
                if old_string and old_string in new_content:
                    new_content = new_content.replace(old_string, new_string, 1)
                elif not old_content and new_string:
                    new_content = (
                        new_content + "\n" + new_string if new_content else new_string
                    )
        elif tool_name == "Update":
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                except Exception:
                    old_content = ""
            new_content = tool_input.get("content", "")

        return old_content, new_content

    @staticmethod
    def handle_implementation_file(
        tdd_context: Dict[str, Any], test_framework: Optional[str], file_path: str
    ) -> Dict[str, Any]:
        """Pure function for implementation file validation with framework-specific suggestions."""

        test_results = tdd_context.get("test_results", {})

        # Filter out validator test failures - only consider APPLICATION test failures
        has_application_failing_tests = (
            TDDValidationPureFunctions.has_application_test_failures(test_results)
        )

        # Approve implementation only for APPLICATION test failures
        if has_application_failing_tests:
            return {
                "approved": True,
                "reason": "TDD GREEN phase: Implementation allowed to fix failing application tests.",
                "tdd_phase": "green",
                "suggestions": [],
            }

        # Build framework-specific suggestions
        suggestions = ["Add a failing test first (Red phase)"]
        if test_framework == "pytest":
            test_file = file_path.replace(".py", "_test.py")
            suggestions.append(f"Run: pytest {test_file} -xvs")
            suggestions.append(
                "Write test using pytest fixtures and parametrize for edge cases"
            )
        elif test_framework == "jest":
            suggestions.append(f"Run: npm test {file_path}")
            suggestions.append("Use describe/it blocks and expect assertions")
        elif test_framework == "go test":
            suggestions.append("Run: go test -v ./...")
            suggestions.append("Create _test.go file with Test* functions")
        elif test_framework == "cargo test":
            suggestions.append("Run: cargo test")
            suggestions.append("Add #[test] functions in a tests module")
        else:
            suggestions.append("Ensure tests are running and capturing failures")

        # Block implementation without failing APPLICATION tests
        return {
            "approved": False,
            "reason": "Implementation change without a failing test.",
            "tdd_phase": "refactor",
            "suggestions": suggestions,
        }

    @staticmethod
    def has_application_test_failures(test_results: Dict[str, Any]) -> bool:
        """Pure function to check for application test failures (filtering out validator tests)."""

        # Check test failures
        if test_results and test_results.get("failures"):
            application_failures = []
            for failure in test_results.get("failures", []):
                test_file = failure.get("file", "")
                test_name = failure.get("test", "")

                # Skip validator's own test failures
                if (
                    "test_tdd_enforcement" in test_file
                    or "test_security_patterns" in test_file
                    or "test_" in test_name
                    and "validator" in test_name.lower()
                    or "cc_validator" in test_file
                    or "test_language_suggestions"
                    in test_file  # Skip language suggestion tests
                    or "tests/" in test_file
                    and any(
                        pattern in test_file
                        for pattern in [
                            "test_tdd",
                            "test_security",
                            "test_integration",
                            "test_specialized",
                            "test_dashboard",
                        ]
                    )
                ):
                    continue

                application_failures.append(failure)

            if len(application_failures) > 0:
                return True

        # Check collection errors (filter out validator tests)
        if test_results and test_results.get("collection_errors"):
            app_collection_errors = []
            for error in test_results.get("collection_errors", []):
                error_str = str(error)
                if not any(
                    pattern in error_str
                    for pattern in [
                        "cc_validator",
                        "tests/tdd/",
                        "tests/security/",
                        "tests/integration/",
                        "tests/specialized/",
                        "tests/unit/",
                    ]
                ):
                    app_collection_errors.append(error)
            if len(app_collection_errors) > 0:
                return True

        return False


def analyze_test_changes(
    old_content: str, new_content: str, file_path: str, tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze changes to test files and return test change information.
    """
    if tool_name is None:
        tool_name = "Update" if old_content else "Write"

    if tool_name == "Update" and not old_content:
        tool_name = "Write"

    if tool_name == "Write":
        new_test_count = count_test_functions(new_content)
        if new_test_count > 1:
            return {
                "approved": False,
                "reason": f"TDD: Multiple tests ({new_test_count}) in new file. Only ONE test per operation allowed.",
                "test_count": new_test_count,
                "tdd_phase": "red",
                "suggestions": [
                    "Write only one failing test at a time",
                    "Follow Red-Green-Refactor cycle",
                    "Split into multiple operations if multiple tests needed",
                ],
            }
        elif new_test_count == 1:
            return {
                "approved": True,
                "reason": "TDD RED phase: Single new test allowed.",
                "test_count": new_test_count,
                "tdd_phase": "red",
                "suggestions": [],
            }
        else:
            return {
                "approved": True,
                "reason": "TDD: No tests found in file.",
                "test_count": 0,
                "tdd_phase": "skipped",
                "suggestions": [],
            }

    else:  # Update, Edit, or MultiEdit operation
        old_test_count = count_test_functions(old_content)
        new_test_count = count_test_functions(new_content)
        net_new_tests = new_test_count - old_test_count

        if net_new_tests > 1:
            return {
                "approved": False,
                "reason": f"TDD: Multiple new tests ({net_new_tests}) added. Only ONE test per operation allowed.",
                "test_count": net_new_tests,
                "tdd_phase": "red",
                "suggestions": [
                    "Add only one failing test at a time",
                    "Follow Red-Green-Refactor cycle",
                    "Split into multiple operations if multiple tests needed",
                ],
            }
        elif net_new_tests == 1:
            return {
                "approved": True,
                "reason": "TDD RED phase: Single new test added.",
                "test_count": net_new_tests,
                "tdd_phase": "red",
                "suggestions": [],
            }
        elif net_new_tests == 0:
            return {
                "approved": True,
                "reason": "TDD REFACTOR phase: Test modification without adding new tests.",
                "test_count": net_new_tests,
                "tdd_phase": "refactor",
                "suggestions": [],
            }
        else:  # net_new_tests < 0 (tests removed)
            return {
                "approved": True,
                "reason": f"TDD REFACTOR phase: {abs(net_new_tests)} test(s) removed/refactored.",
                "test_count": net_new_tests,
                "tdd_phase": "refactor",
                "suggestions": [],
            }


@processor.part_processor_function
async def unified_security_tdd_processor(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """
    100% Native processor for unified Security + TDD validation.
    No custom base classes - pure genai-processors pattern.
    """
    tool_input_data = _extract_tool_input_data_safe(part)
    if not tool_input_data:
        yield part
        return

    tool_name = tool_input_data.tool_name
    tool_input = tool_input_data.tool_input

    # Handle TodoWrite optimization using canonical patterns
    if tool_name == "TodoWrite":
        file_storage = FileStorage()
        todos = tool_input.get("todos", [])
        file_storage.store_todo_state({"todos": todos})

        # Create response using canonical ValidationResponse dataclass
        validation_result = CanonicalValidationResponse(
            approved=True,
            reason="TodoWrite operations are metadata and don't require validation",
            suggestions=[],
            validation_pipeline="native_processor_100",
            detailed_analysis="TodoWrite operations are planning metadata that provide context for future validations. They are automatically approved to maintain developer flow.",
        )

        result_part = create_part_from_dataclass(validation_result)
        if result_part:
            yield result_part
            return

        data: Dict[str, Any] = {"tool_name": tool_name, "tool_input": tool_input}
        data["final_validation_result"] = {
            "approved": True,
            "reason": "TodoWrite operations are metadata and don't require validation",
            "suggestions": [],
            "validation_pipeline": "native_processor_100",
            "security_approved": True,
            "tdd_approved": True,
            "tool_name": tool_name,
            "detailed_analysis": "TodoWrite operations are planning metadata that provide context for future validations. They are automatically approved to maintain developer flow.",
        }

        data["approved"] = True
        data["reason"] = (
            "TodoWrite operations are metadata and don't require validation"
        )
        data["suggestions"] = []

        # Use canonical ValidationResponse dataclass for TodoWrite response
        todo_response = CanonicalValidationResponse(
            approved=True,
            reason="TodoWrite operations are metadata and don't require validation",
            suggestions=[],
            validation_pipeline="native_processor_100",
            detailed_analysis="TodoWrite operations are planning metadata that provide context for future validations. They are automatically approved to maintain developer flow.",
        )

        result_part = create_part_from_dataclass(todo_response)
        if result_part:
            yield result_part
        else:
            # Fix the dataclass issue instead of falling back
            todo_response = CanonicalValidationResponse(
                approved=True,
                reason="TodoWrite operations are automatically approved for developer flow",
                suggestions=[],
                detailed_analysis="TodoWrite operations are planning metadata that provide context for future validations. They are automatically approved to maintain developer flow.",
            )
            result_part = create_part_from_dataclass(todo_response)
            yield result_part
        return

    # Step 1: Security Validation
    security_result = validate_security_pure(tool_name, tool_input)

    # Step 2: TDD Validation (only if security passes)
    if security_result["approved"]:
        file_storage = FileStorage()
        tdd_context = file_storage.get_tdd_context()
        tdd_result = validate_tdd_pure(tool_name, tool_input, tdd_context)
    else:
        tdd_result = {
            "approved": True,
            "reason": "TDD validation skipped due to security concerns",
            "tdd_phase": "skipped",
            "suggestions": [],
        }

    # Step 3: Aggregate Results
    overall_approved = security_result["approved"] and tdd_result["approved"]

    # Determine primary blocking reason and create error substreams for failures
    if not security_result["approved"]:
        primary_reason = f"Security: {security_result['reason']}"
        suggestions = security_result.get("suggestions", [])

        # Yield security error with substream routing
        security_error_part = content_api.ProcessorPart(
            f"Security validation failed: {security_result['reason']}",
            substream_name="error",
        )
        yield security_error_part

    elif not tdd_result["approved"]:
        primary_reason = f"TDD: {tdd_result['reason']}"
        suggestions = tdd_result.get("suggestions", [])

        # Yield TDD error with substream routing
        tdd_error_part = content_api.ProcessorPart(
            f"TDD validation failed: {tdd_result['reason']}", substream_name="error"
        )
        yield tdd_error_part

    else:
        primary_reason = "Operation approved by both security and TDD validation"
        suggestions = []

    # Build detailed analysis
    analysis_parts = []
    if security_result.get("reason"):
        analysis_parts.append(f"Security Analysis:\n{security_result['reason']}")
    if tdd_result.get("reason"):
        analysis_parts.append(f"TDD Compliance Analysis:\n{tdd_result['reason']}")

    security_status = "PASSED" if security_result.get("approved") else "BLOCKED"
    tdd_status = "PASSED" if tdd_result.get("approved") else "BLOCKED"

    analysis_parts.append(
        f"Validation Summary:\nSecurity Validation: {security_status}\nTDD Validation: {tdd_status}"
    )

    if overall_approved:
        analysis_parts.append(
            "Overall Decision: APPROVED - Operation meets both security and TDD requirements"
        )
    else:
        analysis_parts.append(
            "Overall Decision: BLOCKED - Operation failed validation requirements"
        )

    detailed_analysis = "\n\n".join(analysis_parts)

    final_result = {
        "approved": overall_approved,
        "reason": primary_reason,
        "suggestions": suggestions,
        "validation_pipeline": "native_processor_100",
        "security_approved": security_result["approved"],
        "tdd_approved": tdd_result["approved"],
        "tool_name": tool_name,
        "detailed_analysis": detailed_analysis,
        "security_analysis": {
            "approved": security_result["approved"],
            "threats_detected": not security_result["approved"],
            "detailed_analysis": security_result["reason"],
        },
        "tdd_analysis": {
            "approved": tdd_result["approved"],
            "tdd_phase": tdd_result.get("tdd_phase", "unknown"),
            "detailed_analysis": tdd_result["reason"],
        },
    }

    # Add TDD-specific fields when available
    if "test_count" in tdd_result:
        final_result["test_count"] = tdd_result["test_count"]
    if "tdd_phase" in tdd_result:
        final_result["tdd_phase"] = tdd_result["tdd_phase"]

    # Use the dictionary format that the aggregator expects
    # Add error substream for failed validations to enable switch routing
    if not overall_approved:
        error_result_part = content_api.ProcessorPart(
            f"Validation failed: {primary_reason}", substream_name="error"
        )
        yield error_result_part

    # Create the main result part using proper dataclass
    final_validation_data = FinalValidationResultData(
        approved=overall_approved,
        reason=primary_reason,
        suggestions=suggestions,
        validation_pipeline="native_processor_100",
        security_approved=security_result["approved"],
        tdd_approved=tdd_result["approved"],
        detailed_analysis=detailed_analysis,
        security_analysis=security_result.get(
            "reason", "Security validation completed"
        ),
        tdd_analysis=tdd_result.get("reason", "TDD validation completed"),
        tool_name=tool_name,
        test_count=tdd_result.get("test_count"),
        tdd_phase=tdd_result.get("tdd_phase"),
    )

    result_part = create_part_from_dataclass(final_validation_data)
    if result_part:
        yield result_part
    else:
        # Fix the dataclass issue instead of falling back
        final_validation_data = FinalValidationResultData(
            approved=overall_approved,
            reason=primary_reason,
            suggestions=suggestions,
            validation_pipeline="native_processor_100",
            security_approved=security_result["approved"],
            tdd_approved=tdd_result["approved"],
            detailed_analysis=detailed_analysis,
        )
        result_part = create_part_from_dataclass(final_validation_data)
        yield result_part
    return

    # Use canonical FinalValidationResultData dataclass
    final_validation_data = FinalValidationResultData(
        approved=overall_approved,
        reason=primary_reason,
        suggestions=suggestions,
        validation_pipeline="native_processor_100",
        security_approved=security_result["approved"],
        tdd_approved=tdd_result["approved"],
        tool_name=tool_name,
        detailed_analysis=detailed_analysis,
        security_analysis=f"Security Analysis: {security_result.get('reason', 'No analysis available')}",
        tdd_analysis=f"TDD Analysis: {tdd_result.get('reason', 'No analysis available')}",
        test_count=final_result.get("test_count"),
        tdd_phase=final_result.get("tdd_phase"),
    )

    result_part = create_part_from_dataclass(final_validation_data)
    if result_part:
        # Add error substream for failed validations to enable switch routing
        if not overall_approved:
            error_result_part = content_api.ProcessorPart(
                f"Final validation failed: {primary_reason}", substream_name="error"
            )
            yield error_result_part

            # DON'T set error substream on the result part itself to ensure it reaches final extraction
            # The result part needs to reach the canonical pipeline for proper reason extraction
        yield result_part
    else:
        data = {"tool_name": tool_name, "tool_input": tool_input}

        data["final_validation_result"] = final_result

        data.update(
            {
                "approved": overall_approved,
                "reason": primary_reason,
                "suggestions": suggestions,
            }
        )

        # Add error substream for failed validations to enable switch routing
        if not overall_approved:
            error_fallback_part = content_api.ProcessorPart(
                f"Final validation fallback failed: {primary_reason}",
                substream_name="error",
            )
            yield error_fallback_part

        # Try to create another FinalValidationResultData for the fallback case
        fallback_validation_data = FinalValidationResultData(
            approved=overall_approved,
            reason=primary_reason,
            suggestions=suggestions,
            validation_pipeline="native_processor_fallback",
            security_approved=data.get("security_approved", False),
            tdd_approved=data.get("tdd_approved", False),
            tool_name=tool_name,
            detailed_analysis=data.get(
                "detailed_analysis", "Fallback validation result"
            ),
        )

        final_part = create_part_from_dataclass(fallback_validation_data)
        if final_part:
            yield final_part
        else:
            # Last resort: create minimal result
            minimal_result = FinalValidationResultData(
                approved=overall_approved,
                reason=primary_reason,
                suggestions=suggestions,
                validation_pipeline="native_processor_minimal",
                security_approved=False,
                tdd_approved=False,
                detailed_analysis="Minimal fallback validation result",
            )
            final_part = create_part_from_dataclass(minimal_result)
            yield final_part
