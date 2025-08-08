#!/usr/bin/env python3

import asyncio
import sys
from typing import Optional, Dict, Any

from .security_validator import SecurityValidator
from .tdd_pipeline import TDDValidationPipeline
from .file_storage import FileStorage


class HybridValidator:
    """
    HybridValidator orchestrates sequential validation pipeline:
    Stage 1: Security validation (preserve existing security strengths)
    Stage 2: TDD validation (add TDD compliance enforcement)
    Stage 3: Result aggregation (unified comprehensive response)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        data_dir: str = ".claude/cc-validator/data",
    ):
        self.api_key = api_key

        # Initialize validators with API key
        self.security_validator = SecurityValidator(api_key)
        self.tdd_pipeline = TDDValidationPipeline(api_key)

        # Initialize file storage
        self.file_storage = FileStorage(data_dir)
        self.file_storage.cleanup_expired_data()

    async def validate_tool_use(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Main validation entry point for hybrid security + TDD validation.

        Args:
            tool_name: The Claude tool being executed (Bash, Write, Edit, etc.)
            tool_input: The tool's input parameters
            context: Conversation context from transcript

        Returns:
            Comprehensive validation response with security and TDD analysis
        """

        # Skip validation for TodoWrite - just persist and approve
        if tool_name == "TodoWrite":
            todos = tool_input.get("todos", [])

            # Store state
            self.file_storage.store_todo_state({"todos": todos})

            return {
                "approved": True,
                "reason": "TodoWrite operations are metadata and don't require validation",
                "suggestions": [],
                "validation_pipeline": "skipped",
                "security_approved": True,
                "tdd_approved": True,
                "tool_name": tool_name,
                "detailed_analysis": "TodoWrite operations are planning metadata that provide context for future validations. They are automatically approved to maintain developer flow.",
            }

        # Store file modification in context
        self.store_operation_context(tool_name, tool_input)

        # Execute both validations in parallel
        security_result, tdd_result = await asyncio.gather(
            self.security_validator.validate(tool_name, tool_input, context),
            self.tdd_pipeline.validate(tool_name, tool_input, context),
        )

        # Stage 3: Aggregate results
        return self.aggregate_validation_results(security_result, tdd_result, tool_name)

    def aggregate_validation_results(
        self,
        security_result: Dict[str, Any],
        tdd_result: Dict[str, Any],
        tool_name: str,
    ) -> Dict[str, Any]:
        """
        Aggregate security and TDD validation results into unified response.

        Args:
            security_result: Result from security validation
            tdd_result: Result from TDD validation
            tool_name: Operation type for context

        Returns:
            Comprehensive validation response combining both analyses
        """

        # Determine overall approval (both must approve)
        overall_approved = security_result.get("approved", False) and tdd_result.get(
            "approved", False
        )

        # Determine primary blocking reason - show both if both fail
        security_approved = security_result.get("approved", False)
        tdd_approved = tdd_result.get("approved", False)

        if not security_approved and not tdd_approved:
            # Both failed - show both reasons
            security_reason = security_result.get(
                "reason", "Security validation failed"
            )
            tdd_reason = tdd_result.get("reason", "TDD validation failed")
            primary_reason = f"Security: {security_reason} | TDD: {tdd_reason}"
        elif not security_approved:
            primary_reason = f"Security: {security_result.get('reason', 'Security validation failed')}"
        elif not tdd_approved:
            primary_reason = f"TDD: {tdd_result.get('reason', 'TDD validation failed')}"
        else:
            primary_reason = "Operation approved by both security and TDD validation"

        # Combine suggestions from both validators
        combined_suggestions = []
        combined_suggestions.extend(security_result.get("suggestions", []))
        combined_suggestions.extend(tdd_result.get("suggestions", []))

        # Build comprehensive response
        aggregated_response = {
            # Core decision fields
            "approved": overall_approved,
            "reason": primary_reason,
            "suggestions": combined_suggestions,
            # Detailed analysis sections
            "security_analysis": self.extract_security_analysis(security_result),
            "tdd_analysis": self.extract_tdd_analysis(tdd_result),
            "detailed_analysis": self.build_combined_analysis(
                security_result, tdd_result
            ),
            # Technical details
            "validation_pipeline": "sequential_hybrid",
            "security_approved": security_result.get("approved", False),
            "tdd_approved": tdd_result.get("approved", False),
            "tool_name": tool_name,
            # Preserve original response fields for compatibility
            "thinking_process": security_result.get("thinking_process"),
            "full_context": security_result.get("full_context"),
            "raw_response": security_result.get("raw_response"),
            "file_analysis": security_result.get("file_analysis"),
            "performance_analysis": security_result.get("performance_analysis"),
            "code_quality_analysis": security_result.get("code_quality_analysis"),
            "alternative_approaches": security_result.get("alternative_approaches", []),
            "severity_breakdown": security_result.get("severity_breakdown"),
        }

        # Add TDD-specific fields when TDD validation was performed
        if tdd_result:
            aggregated_response.update(
                {
                    "tdd_violation_type": tdd_result.get("violation_type"),
                    "test_count": tdd_result.get("test_count"),
                    "tdd_phase": tdd_result.get("tdd_phase"),
                    "affected_files": tdd_result.get("affected_files", []),
                }
            )

        return aggregated_response

    def extract_security_analysis(
        self, security_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract security-specific analysis from security validation result"""
        return {
            "approved": security_result.get("approved", False),
            "threats_detected": not security_result.get("approved", True),
            "detailed_analysis": security_result.get("detailed_analysis"),
            "performance_suggestions": security_result.get("performance_analysis"),
            "code_quality_feedback": security_result.get("code_quality_analysis"),
            "file_analysis": security_result.get("file_analysis"),
        }

    def extract_tdd_analysis(self, tdd_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract TDD-specific analysis from TDD validation result"""
        return {
            "approved": tdd_result.get("approved", True),
            "violation_type": tdd_result.get("violation_type"),
            "test_count": tdd_result.get("test_count"),
            "tdd_phase": tdd_result.get("tdd_phase", "unknown"),
            "detailed_analysis": tdd_result.get("detailed_analysis"),
            "tdd_suggestions": tdd_result.get("suggestions", []),
        }

    def build_combined_analysis(
        self, security_result: Dict[str, Any], tdd_result: Dict[str, Any]
    ) -> str:
        """Build comprehensive analysis combining security and TDD perspectives"""

        analysis_parts = []

        # Security analysis section
        if security_result.get("detailed_analysis"):
            analysis_parts.append("Security Analysis:")
            analysis_parts.append(security_result["detailed_analysis"])

        # TDD analysis section
        if tdd_result.get("detailed_analysis"):
            analysis_parts.append("TDD Compliance Analysis:")
            analysis_parts.append(tdd_result["detailed_analysis"])

        # Combined assessment
        security_status = "PASSED" if security_result.get("approved") else "BLOCKED"
        tdd_status = "PASSED" if tdd_result.get("approved") else "BLOCKED"

        analysis_parts.append("Validation Summary:")
        analysis_parts.append(f"Security Validation: {security_status}")
        analysis_parts.append(f"TDD Validation: {tdd_status}")

        if security_result.get("approved") and tdd_result.get("approved"):
            analysis_parts.append(
                "Overall Decision: APPROVED - Operation meets both security and TDD requirements"
            )
        else:
            analysis_parts.append(
                "Overall Decision: BLOCKED - Operation failed validation requirements"
            )

        return "\n\n".join(analysis_parts)

    def format_security_only_response(
        self, security_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format response when only security validation is performed"""

        # Preserve all security validation fields
        response = dict(security_result)

        # Add hybrid validation metadata
        response.update(
            {
                "validation_pipeline": "security_only",
                "security_approved": security_result.get("approved", False),
                "tdd_approved": None,  # Not evaluated
                "tdd_analysis": None,
            }
        )

        return response

    def store_operation_context(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> None:
        """Store operation context for future TDD validation"""

        # Store file modifications for context
        if tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            file_path = tool_input.get("file_path", "")

            if tool_name == "Edit":
                old_content = tool_input.get("old_string", "")
                new_content = tool_input.get("new_string", "")
                self.file_storage.store_file_modification(
                    file_path, "Edit", old_content, new_content
                )
            elif tool_name == "Write":
                content = tool_input.get("content", "")
                self.file_storage.store_file_modification(
                    file_path, "Write", "", content
                )
            elif tool_name == "MultiEdit":
                # Store summary of multi-edit operation
                edits_summary = (
                    f"MultiEdit with {len(tool_input.get('edits', []))} edits"
                )
                self.file_storage.store_file_modification(
                    file_path, "MultiEdit", "", edits_summary
                )
            elif tool_name == "Update":
                content = tool_input.get("content", "")
                # Read existing content for Update operations
                import os

                old_content = ""
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            old_content = f.read()
                    except Exception:
                        pass
                self.file_storage.store_file_modification(
                    file_path, "Update", old_content, content
                )

        # Store todo operations for workflow tracking
        elif tool_name == "TodoWrite":
            todos = tool_input.get("todos", [])
            self.file_storage.store_todo_state({"todos": todos})

    def before_tool_callback(self, hook_data: Dict[str, Any]) -> int:
        """
        Main hook callback for Claude Code integration.

        Args:
            hook_data: Hook data from Claude Code containing tool information

        Returns:
            0 for approval, 2 for blocking
        """

        try:
            # Extract tool information from hook data
            tool_name = hook_data.get("tool_name", "")
            tool_input = hook_data.get("tool_input", {})
            context = hook_data.get("context", "")

            # Perform hybrid validation
            result = asyncio.run(self.validate_tool_use(tool_name, tool_input, context))

            # Format output for Claude Code
            self.format_validation_output(result)

            # Return exit code
            return 0 if result.get("approved", False) else 2

        except Exception as e:
            # Deny operation and log error
            print(f"Hybrid validation error: {str(e)}", file=sys.stderr)
            return 2

    def format_validation_output(self, result: Dict[str, Any]) -> None:
        """Format validation output for Claude Code display"""

        if not result.get("approved", False):
            # Detailed blocking message
            print("\n" + "=" * 80, file=sys.stderr)
            print("VALIDATION BLOCKED", file=sys.stderr)
            print("=" * 80, file=sys.stderr)

            print(
                f"REASON: {result.get('reason', 'Validation failed')}", file=sys.stderr
            )

            # Validation status
            if result.get("validation_pipeline") == "sequential_hybrid":
                security_status = "PASS" if result.get("security_approved") else "FAIL"
                tdd_status = "PASS" if result.get("tdd_approved") else "FAIL"
                print(
                    f"STATUS: Security={security_status}, TDD={tdd_status}",
                    file=sys.stderr,
                )

            # Suggestions
            suggestions = result.get("suggestions", [])
            if suggestions:
                print("\nSUGGESTIONS:", file=sys.stderr)
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}", file=sys.stderr)

            # Detailed analysis
            if result.get("detailed_analysis"):
                print("\nDETAILED ANALYSIS:", file=sys.stderr)
                print(result["detailed_analysis"], file=sys.stderr)

            print("=" * 80, file=sys.stderr)

        else:
            # Brief approval message
            print(f"Validation: {result.get('reason', 'Approved')}", file=sys.stderr)
