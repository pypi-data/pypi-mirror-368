from typing import Any, Optional, Dict, List
from genai_processors import processor, content_api
from .validation_dataclasses import ValidationResponse, SecurityResult, TDDResult
from .validation_dataclasses import (
    ProcessorError,
    ValidationError,
    SecurityError,
    TDDError,
    ProcessorStatusMessage,
)


def create_status_part(
    message: str,
    processor_name: str = "",
    progress: Optional[float] = None,
    stage: str = "processing",
) -> content_api.ProcessorPart:
    """Create a status message ProcessorPart following canonical patterns"""
    return processor.status(message)


def create_error_part(
    error: str, details: Optional[str] = None
) -> content_api.ProcessorPart:
    """Create an error ProcessorPart"""
    error_msg = f"Error: {error}"
    if details:
        error_msg += f" - {details}"
    return content_api.ProcessorPart(error_msg, substream_name="error")


def create_processor_error_part(
    error_message: str,
    error_type: str = "ProcessorError",
    processor_name: str = "",
    error_code: Optional[str] = None,
    severity: str = "high",
    suggestions: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from ProcessorError dataclass following canonical patterns"""
    error = ProcessorError(
        error_message=error_message,
        error_type=error_type,
        processor_name=processor_name,
        error_code=error_code,
        severity=severity,
        suggestions=suggestions or [],
        context=context or {},
    )
    return content_api.ProcessorPart.from_dataclass(
        dataclass=error, substream_name="error"
    )


def create_validation_error_part(
    message: str,
    code: str,
    severity: str = "high",
    processor_name: str = "",
    suggestions: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from ValidationError dataclass following canonical patterns"""
    error = ValidationError(
        message=message,
        code=code,
        severity=severity,
        processor_name=processor_name,
        suggestions=suggestions or [],
        context=context or {},
    )
    return content_api.ProcessorPart.from_dataclass(
        dataclass=error, substream_name="error"
    )


def create_security_error_part(
    message: str,
    code: str,
    severity: str = "critical",
    security_issue_type: str = "unknown",
    pattern_matched: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from SecurityError dataclass following canonical patterns"""
    error = SecurityError(
        message=message,
        code=code,
        severity=severity,
        security_issue_type=security_issue_type,
        pattern_matched=pattern_matched,
        suggestions=suggestions or [],
        context=context or {},
    )
    return content_api.ProcessorPart.from_dataclass(
        dataclass=error, substream_name="error"
    )


def create_tdd_error_part(
    message: str,
    code: str,
    tdd_phase: str = "unknown",
    violation_type: Optional[str] = None,
    test_count: int = 0,
    suggestions: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from TDDError dataclass following canonical patterns"""
    error = TDDError(
        message=message,
        code=code,
        tdd_phase=tdd_phase,
        violation_type=violation_type,
        test_count=test_count,
        suggestions=suggestions or [],
        context=context or {},
    )
    return content_api.ProcessorPart.from_dataclass(
        dataclass=error, substream_name="error"
    )


def create_status_message_part(
    message: str,
    processor_name: str = "",
    progress: Optional[float] = None,
    stage: str = "processing",
    context: Optional[Dict[str, Any]] = None,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from ProcessorStatusMessage dataclass following canonical patterns"""
    status = ProcessorStatusMessage(
        message=message,
        processor_name=processor_name,
        progress=progress,
        stage=stage,
        context=context or {},
    )
    return content_api.ProcessorPart.from_dataclass(
        dataclass=status, substream_name="status"
    )


def create_validation_response_part(
    response: ValidationResponse,
) -> content_api.ProcessorPart:
    """Create ProcessorPart from ValidationResponse dataclass"""
    return content_api.ProcessorPart.from_dataclass(dataclass=response)


def create_security_result_part(result: SecurityResult) -> content_api.ProcessorPart:
    """Create ProcessorPart from SecurityResult dataclass"""
    return content_api.ProcessorPart.from_dataclass(dataclass=result)


def create_tdd_result_part(result: TDDResult) -> content_api.ProcessorPart:
    """Create ProcessorPart from TDDResult dataclass"""
    return content_api.ProcessorPart.from_dataclass(dataclass=result)
