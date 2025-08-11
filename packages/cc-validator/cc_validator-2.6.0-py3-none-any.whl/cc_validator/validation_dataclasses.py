#!/usr/bin/env python3
"""
Canonical dataclasses for ProcessorPart integration following genai-processors patterns.
These dataclasses enable clean serialization/deserialization with ProcessorPart.from_dataclass()
and part.get_dataclass() methods.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Type, TypeVar

from dataclasses_json import dataclass_json

T = TypeVar("T")


@dataclass_json
@dataclass(frozen=True)
class SecurityValidationResult:
    """Security validation result following canonical patterns."""

    approved: bool
    reason: str
    severity: str = "none"
    threats_detected: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_cli_format(self) -> str:
        """Format for CLI output"""
        status = "✓ APPROVED" if self.approved else "✗ BLOCKED"
        output = f"{status}: {self.reason}"
        if self.threats_detected:
            output += f"\n  Threats: {', '.join(self.threats_detected)}"
        if self.suggestions:
            output += "\n  Suggestions:\n    • " + "\n    • ".join(self.suggestions)
        return output

    def merge_with(
        self, other: "SecurityValidationResult"
    ) -> "SecurityValidationResult":
        """Merge with another security result, taking the most restrictive"""
        return SecurityValidationResult(
            approved=self.approved and other.approved,
            reason=self.reason if not self.approved else other.reason,
            severity=max(
                self.severity,
                other.severity,
                key=lambda x: ["none", "low", "medium", "high", "critical"].index(x),
            ),
            threats_detected=list(set(self.threats_detected + other.threats_detected)),
            suggestions=list(set(self.suggestions + other.suggestions)),
        )

    def calculate_risk_score(self) -> float:
        """Calculate risk score from 0.0 (safe) to 1.0 (critical)"""
        severity_scores = {
            "none": 0.0,
            "low": 0.2,
            "medium": 0.5,
            "high": 0.75,
            "critical": 1.0,
        }
        base_score = severity_scores.get(self.severity, 0.5)
        threat_multiplier = min(1.0 + len(self.threats_detected) * 0.1, 2.0)
        return min(base_score * threat_multiplier, 1.0)


@dataclass_json
@dataclass(frozen=True)
class TDDValidationResult:
    """TDD validation result following canonical patterns."""

    approved: bool
    reason: str
    tdd_phase: str
    test_count: int = 0
    violation_type: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)

    def to_cli_format(self) -> str:
        """Format for CLI output"""
        phase_icons = {
            "red": "🔴",
            "green": "🟢",
            "refactor": "🔵",
            "skipped": "⏭️",
            "unknown": "❓",
        }
        icon = phase_icons.get(self.tdd_phase, "")
        status = "✓ APPROVED" if self.approved else "✗ BLOCKED"
        output = f"{icon} {status} (Phase: {self.tdd_phase}): {self.reason}"
        if self.test_count > 0:
            output += f"\n  Tests: {self.test_count}"
        if self.violation_type:
            output += f"\n  Violation: {self.violation_type}"
        if self.suggestions:
            output += "\n  Suggestions:\n    • " + "\n    • ".join(self.suggestions)
        return output

    def is_tdd_compliant(self) -> bool:
        """Check if TDD workflow is being followed correctly"""
        if self.tdd_phase == "red":
            return self.test_count > 0 and not self.approved
        elif self.tdd_phase == "green":
            return self.test_count > 0 and self.approved
        elif self.tdd_phase == "refactor":
            return self.test_count > 0
        return self.tdd_phase == "skipped"

    def get_phase_transition_advice(self) -> str:
        """Provide advice for next TDD phase"""
        transitions = {
            "red": "Write minimal implementation to make tests pass",
            "green": "Refactor code while keeping tests green",
            "refactor": "Add new failing test for next feature",
            "skipped": "Consider adding tests for better reliability",
            "unknown": "Start with writing a failing test",
        }
        return transitions.get(
            self.tdd_phase, "Follow TDD cycle: Red → Green → Refactor"
        )


@dataclass_json
@dataclass(frozen=True)
class ValidationRequest:
    """Validation request payload following canonical patterns."""

    tool_name: str
    tool_input: Dict[str, Any]
    context: str
    api_key: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class ValidationResponse:
    """Combined validation response following canonical patterns."""

    approved: bool
    reason: str
    suggestions: List[str] = field(default_factory=list)
    security_result: Optional[SecurityValidationResult] = None
    tdd_result: Optional[TDDValidationResult] = None
    validation_pipeline: str = "canonical_processor"
    detailed_analysis: Optional[str] = None

    def to_json_response(self) -> Dict[str, Any]:
        """Convert to JSON response for Claude Code hook"""
        response = {
            "approved": self.approved,
            "reason": self.reason,
            "suggestions": self.suggestions,
            "validation_pipeline": self.validation_pipeline,
        }
        if self.security_result:
            response["security_approved"] = self.security_result.approved
            response["security_severity"] = self.security_result.severity
        if self.tdd_result:
            response["tdd_approved"] = self.tdd_result.approved
            response["tdd_phase"] = self.tdd_result.tdd_phase
            response["test_count"] = self.tdd_result.test_count
        if self.detailed_analysis:
            response["detailed_analysis"] = self.detailed_analysis
        return response

    def get_exit_code(self) -> int:
        """Get exit code for Claude Code hook (0=approved, 2=blocked)"""
        return 0 if self.approved else 2

    def combine_analyses(self) -> str:
        """Combine all analyses into a single detailed report"""
        report = []
        if self.security_result:
            sec_reason = self.security_result.reason
            # Check if already prefixed to avoid duplication
            if not sec_reason.startswith("Security:") and not sec_reason.startswith(
                "Template Security:"
            ):
                sec_reason = f"Security: {sec_reason}"
            report.append(sec_reason)
        if self.tdd_result:
            tdd_reason = self.tdd_result.reason
            # Check if already prefixed to avoid duplication
            if not tdd_reason.startswith("TDD:"):
                tdd_reason = f"TDD: {tdd_reason}"
            report.append(tdd_reason)
        if self.detailed_analysis:
            report.append(f"Analysis: {self.detailed_analysis}")
        return " | ".join(report) if report else self.reason


@dataclass_json
@dataclass(frozen=True)
class FileAnalysis:
    """File analysis result following canonical patterns."""

    file_path: str
    category: str
    requires_tdd: bool
    is_test_file: bool = False
    reason: Optional[str] = None


@dataclass_json
@dataclass
class ProcessingData:
    """Intermediate processing data for security and TDD validation pipelines."""

    tool_name: str
    tool_input: Dict[str, Any]
    context: str = ""
    api_key: Optional[str] = None
    tdd_context: Dict[str, Any] = field(default_factory=dict)
    file_category: Dict[str, Any] = field(default_factory=dict)
    is_tdd_relevant: bool = False
    tool_routing_security_result: Optional[Dict[str, Any]] = None
    bash_security_result: Optional[Dict[str, Any]] = None
    path_security_result: Optional[Dict[str, Any]] = None
    comment_security_result: Optional[Dict[str, Any]] = None
    file_content_security_result: Optional[Dict[str, Any]] = None
    template_security_result: Optional[Dict[str, Any]] = None
    branch_security_result: Optional[Dict[str, Any]] = None
    file_operation_branch_result: Optional[Dict[str, Any]] = None
    file_analysis_result: Optional[Dict[str, Any]] = None
    final_security_result: Optional[Dict[str, Any]] = None
    final_tdd_result: Optional[Dict[str, Any]] = None
    final_validation_result: Optional[Dict[str, Any]] = None


@dataclass_json
@dataclass(frozen=True)
class ProcessorConfig:
    """Processor configuration following canonical patterns."""

    api_key: Optional[str] = None
    model_name: str = "gemini-2.5-pro"
    thinking_budget: int = 24576
    enabled_tools: List[str] = field(
        default_factory=lambda: [
            "Write",
            "Edit",
            "Bash",
            "MultiEdit",
            "Update",
            "TodoWrite",
        ]
    )
    secret_keywords: List[str] = field(
        default_factory=lambda: ["password", "api_key", "secret", "token", "credential"]
    )
    pii_fields: List[str] = field(
        default_factory=lambda: ["email", "phone", "ssn", "credit_card", "address"]
    )


@dataclass_json
@dataclass(frozen=True)
class ProcessorStatus:
    """Status update from processor following canonical patterns."""

    message: str
    processor_name: str = ""
    progress: Optional[float] = None


@dataclass_json
@dataclass(frozen=True)
class ProcessorError:
    """Error from processor following canonical patterns."""

    error_message: str
    error_type: str = "ProcessorError"
    processor_name: str = ""
    error_code: Optional[str] = None
    severity: str = "high"
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_exception(self) -> Exception:
        """Convert to Python exception for raising"""
        msg = f"[{self.processor_name}] {self.error_message}"
        if self.error_code:
            msg = f"{msg} (Code: {self.error_code})"
        return RuntimeError(msg)

    def to_validation_result(self) -> Dict[str, Any]:
        """Convert error to validation result format"""
        return {
            "approved": False,
            "reason": f"Error: {self.error_message}",
            "suggestions": self.suggestions,
            "error_type": self.error_type,
            "severity": self.severity,
        }

    def is_retryable(self) -> bool:
        """Check if error is retryable based on type"""
        retryable_codes = ["TIMEOUT", "NETWORK", "RATE_LIMIT", "TEMPORARY"]
        return self.error_code in retryable_codes if self.error_code else False


@dataclass_json
@dataclass(frozen=True)
class ValidationError:
    """Validation error following canonical patterns."""

    message: str
    code: str
    severity: str = "high"
    processor_name: str = ""
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class SecurityError:
    """Security validation error following canonical patterns."""

    message: str
    code: str
    severity: str = "critical"
    security_issue_type: str = "unknown"
    pattern_matched: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class TDDError:
    """TDD validation error following canonical patterns."""

    message: str
    code: str
    tdd_phase: str = "unknown"
    violation_type: Optional[str] = None
    test_count: int = 0
    suggestions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class ProcessorStatusMessage:
    """Status message from processor following canonical patterns."""

    message: str
    processor_name: str = ""
    progress: Optional[float] = None
    stage: str = "processing"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class ToolInputData:
    """Tool input data following canonical patterns."""

    tool_name: str
    tool_input: Dict[str, Any]
    context: str = ""
    api_key: Optional[str] = None
    pipeline_initialized: bool = False
    storage_context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class ProcessorResult:
    """Generic processor result following canonical patterns."""

    approved: bool
    reason: str
    processor_type: str
    severity: str = "none"
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_validation_response(self) -> ValidationResponse:
        """Convert to ValidationResponse for pipeline output"""
        return ValidationResponse(
            approved=self.approved,
            reason=self.reason,
            suggestions=self.suggestions,
            validation_pipeline=f"{self.processor_type}_processor",
            detailed_analysis=self.metadata.get("analysis", None),
        )

    def with_metadata(self, **kwargs: Any) -> "ProcessorResult":
        """Create new result with additional metadata"""
        import dataclasses

        new_metadata = {**self.metadata, **kwargs}
        return dataclasses.replace(self, metadata=new_metadata)


@dataclass_json
@dataclass(frozen=True)
class FileCategorizationData:
    """File categorization data following canonical patterns."""

    category: str
    requires_tdd: bool
    is_test_file: bool = False
    reason: Optional[str] = None
    confidence: float = 1.0


@dataclass_json
@dataclass
class TDDContextData:
    """TDD context data following canonical patterns."""

    test_results: Dict[str, Any] = field(default_factory=dict)
    file_modifications: List[Dict[str, Any]] = field(default_factory=list)
    todos: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[str] = None


@dataclass_json
@dataclass
class SecurityProcessorData:
    """Security processor intermediate data following canonical patterns."""

    tool_routing_security_result: Optional[Dict[str, Any]] = None
    bash_security_result: Optional[Dict[str, Any]] = None
    path_security_result: Optional[Dict[str, Any]] = None
    comment_security_result: Optional[Dict[str, Any]] = None
    file_content_security_result: Optional[Dict[str, Any]] = None
    template_security_result: Optional[Dict[str, Any]] = None
    branch_security_result: Optional[Dict[str, Any]] = None
    file_operation_branch_result: Optional[Dict[str, Any]] = None
    file_analysis_result: Optional[Dict[str, Any]] = None
    final_security_result: Optional[Dict[str, Any]] = None


@dataclass_json
@dataclass
class PipelineStateData:
    """Pipeline state management data following canonical patterns."""

    pipeline_initialized: bool = False
    storage_context: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass(frozen=True)
class FinalValidationResultData:
    """Final validation result data following canonical patterns."""

    approved: bool
    reason: str
    suggestions: List[str] = field(default_factory=list)
    validation_pipeline: str = ""
    security_approved: bool = False
    tdd_approved: bool = False
    tool_name: str = ""
    detailed_analysis: str = ""
    security_analysis: str = ""
    tdd_analysis: str = ""
    test_count: Optional[int] = None
    tdd_phase: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class ErrorAggregationData:
    """Error aggregation data following canonical patterns."""

    total_errors: int = 0
    critical_errors: int = 0
    high_errors: int = 0
    primary_error: Optional[Dict[str, Any]] = None
    all_errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass_json
@dataclass
class SecurityResult:
    """Security validation result with threat analysis"""

    approved: bool
    reason: str
    severity: str = "info"
    pattern_matched: Optional[str] = None
    threats_detected: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.suggestions is None:
            self.suggestions = []
        if self.threats_detected is None:
            self.threats_detected = []


@dataclass_json
@dataclass
class TDDResult:
    """TDD validation result with test analysis details"""

    approved: bool
    reason: str
    message: str = ""
    suggestion: Optional[str] = None
    suggestions: Optional[List[str]] = None
    tdd_phase: str = "unknown"
    test_count: Optional[int] = None
    violation_type: Optional[str] = None

    def __post_init__(self) -> None:
        if self.suggestions is None:
            self.suggestions = []
        if self.suggestion and self.suggestion not in self.suggestions:
            self.suggestions.append(self.suggestion)
        if not self.message and self.reason:
            self.message = self.reason


def extract_dataclass_from_part(part: Any, dataclass_type: Type[T]) -> Optional[T]:
    """Extract dataclass from a ProcessorPart using dataclass_json"""
    try:
        if hasattr(part, "text") and part.text:
            data = json.loads(part.text)
            return dataclass_type.from_dict(data)  # type: ignore[attr-defined, no-any-return]
        elif hasattr(part, "json") and part.json:
            return dataclass_type.from_dict(part.json)  # type: ignore[attr-defined, no-any-return]
        else:
            return None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


def get_dataclass_from_part_safe(part: Any, dataclass_type: Type[T]) -> Optional[T]:
    """
    Safely extract dataclass from ProcessorPart using canonical patterns.
    Returns None if extraction fails.
    """
    try:
        if hasattr(part, "get_dataclass"):
            return part.get_dataclass(dataclass_type)  # type: ignore[no-any-return]
        elif hasattr(part, "text") and part.text:
            data = json.loads(part.text)
            return dataclass_type.from_dict(data)  # type: ignore[attr-defined, no-any-return]
        return None
    except (AttributeError, TypeError, ValueError):
        return None


def create_part_from_dataclass(dataclass_instance: Any) -> Optional[Any]:
    """Create ProcessorPart from dataclass using canonical patterns."""
    try:
        from genai_processors import content_api

        return content_api.ProcessorPart.from_dataclass(dataclass=dataclass_instance)
    except (ImportError, AttributeError, TypeError, ValueError) as e:
        # Handle cases where dataclass conversion fails
        if "dataclass" in str(e).lower():
            # This is a dataclass-related error, return None to allow fallback
            return None
        # For other errors, re-raise
        raise


def extract_tool_input_data(part: Any) -> Optional[ToolInputData]:
    """Extract tool input data from ProcessorPart using canonical patterns."""
    try:
        if hasattr(part, "get_dataclass"):
            return part.get_dataclass(ToolInputData)  # type: ignore[no-any-return]
        elif hasattr(part, "text") and part.text:
            data = json.loads(part.text)
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
    except (AttributeError, TypeError, ValueError):
        return None
