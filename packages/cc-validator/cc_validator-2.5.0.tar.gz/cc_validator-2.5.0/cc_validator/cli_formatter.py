"""
CLI output formatting utilities for Claude Code hook responses.

This module handles the complex formatting logic for validation results
that are sent to Claude Code hooks as JSON responses.
"""

from typing import Dict, List, Any


class ClaudeCodeHookFormatter:
    """Formats validation results for Claude Code hook responses."""

    @staticmethod
    def format_permission_response(validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format validation result into Claude Code hook response JSON."""
        is_approved = validation_result.get("approved", False)

        hook_response = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow" if is_approved else "deny",
                "permissionDecisionReason": (
                    ClaudeCodeHookFormatter._build_decision_reason(validation_result)
                    if not is_approved
                    else "Operation approved"
                ),
            }
        }

        return hook_response

    @staticmethod
    def _build_decision_reason(validation_result: Dict[str, Any]) -> str:
        """Build the detailed decision reason text from validation result."""
        reason_parts = []

        # Add main reason
        reason = validation_result.get("reason", "Operation blocked")
        reason_parts.append(f"❌ {reason}")

        # Add suggestions
        if validation_result.get("suggestions"):
            reason_parts.append("")  # Empty line
            for suggestion in validation_result.get("suggestions", []):
                reason_parts.append(f"→ {suggestion}")

        # Collect and add details
        details = ClaudeCodeHookFormatter._collect_details(validation_result)
        if details:
            reason_parts.append("\nDetails:")
            for detail in details:
                reason_parts.append(f"• {detail}")

        # Add severity breakdown
        ClaudeCodeHookFormatter._add_severity_breakdown(validation_result, reason_parts)

        # Add file-specific analysis
        ClaudeCodeHookFormatter._add_file_analysis(validation_result, reason_parts)

        return "\n".join(reason_parts)

    @staticmethod
    def _collect_details(validation_result: Dict[str, Any]) -> List[str]:
        """Collect detailed analysis information."""
        details = []

        if validation_result.get("detailed_analysis"):
            details.append(str(validation_result.get("detailed_analysis")))
        if validation_result.get("performance_analysis"):
            details.append(str(validation_result.get("performance_analysis")))
        if validation_result.get("code_quality_analysis"):
            details.append(str(validation_result.get("code_quality_analysis")))

        return details

    @staticmethod
    def _add_severity_breakdown(
        validation_result: Dict[str, Any], reason_parts: List[str]
    ) -> None:
        """Add severity breakdown information to reason parts."""
        if validation_result.get("severity_breakdown"):
            breakdown = validation_result.get("severity_breakdown")
            if breakdown:
                issues = []
                if hasattr(breakdown, "BLOCK") and breakdown.BLOCK:
                    issues.extend(breakdown.BLOCK)
                elif isinstance(breakdown, dict) and breakdown.get("BLOCK"):
                    issues.extend(breakdown["BLOCK"])

                if issues:
                    reason_parts.append("\nSpecific issues:")
                    for issue in issues:
                        reason_parts.append(f"• {issue}")

    @staticmethod
    def _add_file_analysis(
        validation_result: Dict[str, Any], reason_parts: List[str]
    ) -> None:
        """Add file-specific analysis information to reason parts."""
        if validation_result.get("file_analysis"):
            file_analysis = validation_result.get("file_analysis")

            # Add file-specific issues
            file_issues = []
            if file_analysis and file_analysis.get("security_issues"):
                file_issues.extend(file_analysis.get("security_issues", []))
            if file_analysis and file_analysis.get("code_quality_concerns"):
                file_issues.extend(file_analysis.get("code_quality_concerns", []))

            if file_issues:
                reason_parts.append("\nFile issues found:")
                for issue in file_issues:
                    reason_parts.append(f"• {issue}")

            # Add unique recommendations
            if file_analysis and file_analysis.get("recommendations"):
                recs = file_analysis.get("recommendations", [])
                main_suggestions = validation_result.get("suggestions", [])
                unique_recs = [r for r in recs if r not in main_suggestions]
                if unique_recs:
                    reason_parts.append("\nAdditional recommendations:")
                    for rec in unique_recs:
                        reason_parts.append(f"→ {rec}")

    @staticmethod
    def format_error_response(
        error_message: str, allow_operation: bool = False
    ) -> Dict[str, Any]:
        """Format error message into Claude Code hook response JSON."""
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow" if allow_operation else "deny",
                "permissionDecisionReason": error_message,
            }
        }
