#!/usr/bin/env python3
"""
SecurityValidator class that wraps the processor-based validation architecture.
"""

from typing import Dict, Any, Optional

from pydantic import BaseModel

# Branch validation enforcement flag - can be disabled for testing
ENFORCE_ISSUE_WORKFLOW = True


class ValidationResponse(BaseModel):
    """Structured validation response for security operations."""

    approved: bool
    threats_detected: Optional[list] = None
    severity: str = "none"
    reason: str = ""
    suggestions: list = []


class SecurityValidator:
    """Security validation wrapper for the processor-based validation pipeline."""

    def __init__(
        self, api_key: Optional[str] = None, data_dir: str = ".claude/cc-validator/data"
    ):
        self.api_key = api_key
        self.data_dir = data_dir
        self.client = None

    def validate_tool_use(
        self, tool_name: str, tool_input: Dict[str, Any], context: str = ""
    ) -> Dict[str, Any]:
        """Main validation entry point that delegates to processor pipeline."""
        try:
            if (
                tool_name in ["Write", "Edit", "MultiEdit", "Update"]
                and "content" in tool_input
            ):
                file_path = tool_input.get("file_path", "")
                content = tool_input.get("content", "")

                from .file_categorization import FileContextAnalyzer

                file_info = FileContextAnalyzer.categorize_file(file_path, content)
                is_code_file = file_info.get("category") not in [
                    "docs",
                    "data",
                    "template",
                    "config",
                    "test",
                ]

                if is_code_file and len(content) > 500:
                    self.upload_file_for_analysis(file_path, content)

            from .canonical_pipeline import CanonicalPipelineValidator
            from .file_storage import FileStorage

            file_storage = FileStorage()
            validator = CanonicalPipelineValidator(file_storage)
            result = validator.validate_tool_use(tool_name, tool_input, context)

            # Extract security-specific result if available
            if "final_security_result" in result and isinstance(
                result["final_security_result"], dict
            ):
                security_result = result["final_security_result"]
                return {
                    "approved": security_result.get(
                        "approved", result.get("approved", False)
                    ),
                    "reason": security_result.get("reason", result.get("reason", "")),
                    "threats_detected": not security_result.get("approved", True),
                    "security_details": security_result.get("security_details", {}),
                    "suggestions": result.get("suggestions", []),
                    "severity": security_result.get(
                        "severity",
                        "high" if not security_result.get("approved", True) else "none",
                    ),
                }
            elif "security_analysis" in result:
                # Handle case where security_analysis might be passed as a dict (backward compatibility)
                security_data = result["security_analysis"]
                if isinstance(security_data, dict):
                    return {
                        "approved": security_data.get(
                            "approved", result.get("approved", False)
                        ),
                        "reason": security_data.get(
                            "detailed_analysis", result.get("reason", "")
                        ),
                        "threats_detected": security_data.get(
                            "threats_detected", not security_data.get("approved", True)
                        ),
                        "security_details": security_data.get("security_details", {}),
                        "suggestions": result.get("suggestions", []),
                        "severity": (
                            "high"
                            if not security_data.get("approved", True)
                            else "none"
                        ),
                    }

            # Fallback to general result
            return {
                "approved": result.get("approved", False),
                "reason": result.get("reason", "Validation completed"),
                "threats_detected": not result.get("approved", False),
                "security_details": {},
                "suggestions": result.get("suggestions", []),
                "severity": "high" if not result.get("approved", False) else "none",
            }

        except Exception as e:
            return {
                "approved": False,
                "reason": f"Security validation error: {str(e)}",
                "threats_detected": True,
                "security_details": {"error": str(e)},
                "suggestions": ["Check security validation configuration"],
                "severity": "high",
            }

    def validate_file_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """File operation validation method."""
        file_path = operation.get("file_path", "")

        branch_result = self._check_branch_validation(file_path)
        if branch_result is not None:
            return branch_result

        # If branch validation passes, return approved
        return {
            "approved": True,
            "reason": "File operation allowed",
            "suggestions": [],
        }

    def _get_current_branch(self) -> Optional[str]:
        """
        Get the current git branch name.
        """
        import subprocess
        import os

        # Test override for unit tests
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
                # Return None for detached HEAD state
                if branch == "HEAD":
                    return None
                return branch
        except Exception:
            pass
        return None

    def _is_protected_branch(self, branch_name: Optional[str] = None) -> bool:
        """
        Check if a branch is protected (main/master).
        """
        if branch_name is None:
            branch_name = self._get_current_branch()
        if not branch_name:
            return False
        protected_branches = ["main", "master"]
        return branch_name in protected_branches

    def _is_allowed_file_on_main(self, file_path: str) -> bool:
        """
        Check if a file is allowed to be modified on main branch.
        """
        import os

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

    def _extract_issue_number(self, branch_name: str) -> Optional[str]:
        """
        Extract issue number from branch name (e.g., "123-feature" -> "123").
        """
        import re

        if not branch_name:
            return None
        match = re.match(r"^(\d+)-", branch_name)
        if match:
            return match.group(1)
        return None

    def _validate_issue_exists(self, issue_number: str) -> bool:
        """
        Check if a GitHub issue exists.
        """
        import subprocess

        try:
            result = subprocess.run(
                ["gh", "issue", "view", issue_number],
                capture_output=True,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return result.returncode == 0
        except FileNotFoundError:
            # gh CLI not installed - assume issue exists
            return True
        except Exception:
            return False

    def _get_issue_workflow_suggestions(self, branch_name: str) -> list:
        """Get issue workflow suggestions for a branch name."""
        issue_number = self._extract_issue_number(branch_name)

        if issue_number and not self._validate_issue_exists(issue_number):
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

    def _check_branch_validation(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Check branch validation for a file path."""
        # Skip validation if disabled
        if not ENFORCE_ISSUE_WORKFLOW:
            return None

        current_branch = self._get_current_branch()

        # Skip validation if branch detection fails
        if current_branch is None:
            return None

        # Check if working on protected branch
        if self._is_protected_branch(current_branch):
            # Allow certain file types on protected branches
            if self._is_allowed_file_on_main(file_path):
                return None  # Allowed - return None as per test expectation
            else:
                return {
                    "approved": False,
                    "reason": f"Direct modifications to protected branch '{current_branch}' are not allowed",
                    "suggestions": [
                        "Create a feature branch for your changes",
                        "Use pull requests to merge changes to main",
                    ],
                }

        # Validate issue-based branch naming
        issue_number = self._extract_issue_number(current_branch)
        if issue_number and not self._validate_issue_exists(issue_number):
            return {
                "approved": False,
                "reason": f"Branch references non-existent issue #{issue_number}",
                "suggestions": [
                    f"Create issue #{issue_number} before continuing",
                    "Use existing issue numbers for branch names",
                ],
            }

        return None  # Validation passed - return None as per test expectation

    def validate(
        self, tool_name: str, tool_input: Dict[str, Any], context: str = ""
    ) -> Dict[str, Any]:
        """Validate tool use (alias for validate_tool_use)."""
        return self.validate_tool_use(tool_name, tool_input, context)

    def upload_file_for_analysis(self, file_path: str, content: str) -> None:
        """Upload file for analysis (no-op in processor architecture)."""
        pass
