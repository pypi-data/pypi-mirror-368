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
