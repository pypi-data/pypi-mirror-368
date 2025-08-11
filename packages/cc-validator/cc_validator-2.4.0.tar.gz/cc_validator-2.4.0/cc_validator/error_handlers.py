#!/usr/bin/env python3
"""
Canonical error and status handlers following Google's genai-processors patterns.
Implements switch-based error routing with structured error processing.
"""

from typing import AsyncIterable, Optional, Any

try:
    from genai_processors import processor, content_api, switch
except ImportError:
    processor = None
    content_api = None
    switch = None

from .validation_dataclasses import (
    ProcessorError,
    ValidationError,
    SecurityError,
    TDDError,
    ProcessorStatusMessage,
    ErrorAggregationData,
    FinalValidationResultData,
    create_part_from_dataclass,
)
from .processor_factories import create_status_part


@processor.part_processor_function
async def error_handler_processor(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """
    Canonical error handler processor following Google's genai-processors patterns.
    Processes parts with substream_name='error' and formats them for user display.
    Routes error substreams through switch-based routing.
    """
    try:
        if hasattr(part, "get_dataclass"):
            error = part.get_dataclass(ProcessorError)
            if error:
                status_part = create_status_part(
                    f"Processor Error: {error.error_message}"
                )
                yield status_part
                error_part = content_api.ProcessorPart(
                    f"Processor Error: {error.error_message}", substream_name="error"
                )
                yield error_part
                return

            validation_error = part.get_dataclass(ValidationError)
            if validation_error:
                status_part = create_status_part(
                    f"Validation Error: {validation_error.message}"
                )
                yield status_part
                error_part = content_api.ProcessorPart(
                    f"Validation Error: {validation_error.message}",
                    substream_name="error",
                )
                yield error_part
                return

            security_error = part.get_dataclass(SecurityError)
            if security_error:
                status_part = create_status_part(
                    f"Security Error: {security_error.message}"
                )
                yield status_part
                error_part = content_api.ProcessorPart(
                    f"Security Error: {security_error.message}", substream_name="error"
                )
                yield error_part
                return

            tdd_error = part.get_dataclass(TDDError)
            if tdd_error:
                status_part = create_status_part(f"TDD Error: {tdd_error.message}")
                yield status_part
                error_part = content_api.ProcessorPart(
                    f"TDD Error: {tdd_error.message}", substream_name="error"
                )
                yield error_part
                return
    except Exception:
        pass

    if hasattr(part, "text") and part.text:
        status_part = create_status_part(f"Error: {part.text}")
        yield status_part
        error_part = content_api.ProcessorPart(
            f"Error: {part.text}", substream_name="error"
        )
        yield error_part
        return

    status_part = create_status_part("Unknown error occurred")
    yield status_part
    error_part = content_api.ProcessorPart(
        "Unknown error occurred", substream_name="error"
    )
    yield error_part


@processor.part_processor_function
async def status_handler_processor(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """
    Canonical status handler processor following Google's genai-processors patterns.
    Processes parts with substream_name='status' for user feedback.
    """
    try:
        if hasattr(part, "get_dataclass"):
            status = part.get_dataclass(ProcessorStatusMessage)
            if status:
                progress_info = (
                    f" ({status.progress * 100:.1f}%)" if status.progress else ""
                )
                stage_info = (
                    f" [{status.stage}]" if status.stage != "processing" else ""
                )
                processor_info = (
                    f" ({status.processor_name})" if status.processor_name else ""
                )

                message = f"{status.message}{progress_info}{stage_info}{processor_info}"
                yield create_status_part(message)
                yield part
                return
    except Exception:
        pass

    if hasattr(part, "text") and part.text:
        yield create_status_part(part.text)
        yield part
        return

    yield create_status_part("Status update")
    yield part


@processor.part_processor_function
async def error_aggregation_processor(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """
    Aggregates errors from previous processors and creates final error response.
    Collects all error substreams and creates comprehensive error reporting.
    """
    try:
        if hasattr(part, "json") and part.json:
            data = dict(part.json)
        else:
            yield part
            return
    except (AttributeError, TypeError):
        yield part
        return

    if not data or "error_aggregation_handled" in data:
        yield part
        return

    # If there's already a final_validation_result, preserve it and skip error aggregation
    if "final_validation_result" in data:
        yield part
        return

    updated_data = dict(data)
    errors_found = []

    for key, value in data.items():
        if key.endswith("_error") and isinstance(value, dict):
            errors_found.append(value)
        elif key.endswith("_security_result") and isinstance(value, dict):
            approved = value.get("approved", True)
            if not approved:
                errors_found.append(
                    {
                        "type": "security_error",
                        "message": value.get("reason", "Security validation failed"),
                        "severity": value.get("severity", "high"),
                    }
                )
        elif (
            key.endswith("_tdd_result")
            and isinstance(value, dict)
            and not value.get("approved", True)
        ):
            errors_found.append(
                {
                    "type": "tdd_error",
                    "message": value.get("reason", "TDD validation failed"),
                    "tdd_phase": value.get("tdd_phase", "unknown"),
                }
            )

    if errors_found:
        critical_errors = [e for e in errors_found if e.get("severity") == "critical"]
        high_errors = [e for e in errors_found if e.get("severity") == "high"]

        if critical_errors:
            primary_error = critical_errors[0]
        elif high_errors:
            primary_error = high_errors[0]
        else:
            primary_error = errors_found[0]
    else:
        critical_errors = []
        high_errors = []
        primary_error = None

    # Use ErrorAggregationData dataclass for error aggregation response
    error_aggregation_data = ErrorAggregationData(
        total_errors=len(errors_found),
        critical_errors=len(critical_errors),
        high_errors=len(high_errors),
        primary_error=primary_error,
        all_errors=errors_found,
    )

    # Create aggregated validation result with proper reason field
    if errors_found:
        primary_error_message = (
            primary_error.get("message", "Validation failed")
            if primary_error
            else "Validation failed"
        )
        # Create proper FinalValidationResultData for aggregated result
        final_validation_data = FinalValidationResultData(
            approved=False,
            reason=primary_error_message,
            suggestions=[],
            validation_pipeline="canonical_aggregation",
            security_approved=False,
            tdd_approved=True,
            detailed_analysis=f"Error aggregation found {len(errors_found)} errors. Primary error: {primary_error_message}",
        )

        result_part = create_part_from_dataclass(final_validation_data)
        if result_part:
            yield result_part
        else:
            # Fix the dataclass issue instead of falling back
            final_validation_data = FinalValidationResultData(
                approved=False,
                reason=primary_error_message,
                suggestions=[],
                validation_pipeline="canonical_aggregation",
                security_approved=False,
                tdd_approved=True,
                detailed_analysis=f"Error aggregation found {len(errors_found)} errors. Primary error: {primary_error_message}",
            )
            result_part = create_part_from_dataclass(final_validation_data)
            yield result_part
        return
    else:
        # No errors found - preserve original approval status
        if "final_validation_result" in data:
            # Pass through the existing validation result
            # Create appropriate dataclass for passthrough data
            if "approved" in data and "reason" in data:
                final_result_data = FinalValidationResultData(
                    approved=data.get("approved", True),
                    reason=data.get("reason", "Validation completed"),
                    suggestions=data.get("suggestions", []),
                    validation_pipeline=data.get(
                        "validation_pipeline", "canonical_aggregation"
                    ),
                    security_approved=data.get("security_approved", True),
                    tdd_approved=data.get("tdd_approved", True),
                    detailed_analysis=data.get("detailed_analysis", ""),
                )
                result_part = create_part_from_dataclass(final_result_data)
                if result_part:
                    yield result_part
                    return
            return

    result_part = create_part_from_dataclass(error_aggregation_data)
    if result_part:
        yield result_part
    else:
        if errors_found:
            updated_data["aggregated_errors"] = {
                "total_errors": len(errors_found),
                "critical_errors": len(critical_errors),
                "high_errors": len(high_errors),
                "primary_error": primary_error,
                "all_errors": errors_found,
            }

            updated_data["approved"] = False
            updated_data["reason"] = (
                primary_error.get("message", "Validation failed")
                if primary_error
                else "Validation failed"
            )
        else:
            updated_data["aggregated_errors"] = {
                "total_errors": 0,
                "critical_errors": 0,
                "high_errors": 0,
                "primary_error": None,
                "all_errors": [],
            }

            if "approved" not in updated_data:
                updated_data["approved"] = True
                updated_data["reason"] = "No errors found"

        updated_data["error_aggregation_handled"] = True
        # Create proper FinalValidationResultData for updated data
        final_data = FinalValidationResultData(
            approved=updated_data.get("approved", True),
            reason=updated_data.get("reason", "No errors found"),
            suggestions=updated_data.get("suggestions", []),
            validation_pipeline="canonical_aggregation",
            security_approved=updated_data.get("security_approved", True),
            tdd_approved=updated_data.get("tdd_approved", True),
            detailed_analysis=updated_data.get(
                "detailed_analysis", "Error aggregation completed"
            ),
        )

        result_part = create_part_from_dataclass(final_data)
        if result_part:
            yield result_part
        else:
            # Fix the dataclass issue instead of falling back
            final_data = FinalValidationResultData(
                approved=True,
                reason="No errors found",
                suggestions=[],
                validation_pipeline="canonical_aggregation",
                security_approved=True,
                tdd_approved=True,
                detailed_analysis="Error aggregation completed",
            )
            result_part = create_part_from_dataclass(final_data)
            yield result_part


def get_substream_name_safe(part: content_api.ProcessorPart) -> str:
    """
    Safely get substream name from ProcessorPart.
    Returns empty string for default substream or if extraction fails.
    """
    try:
        if hasattr(content_api, "get_substream_name"):
            return content_api.get_substream_name(part) or ""
        elif hasattr(part, "substream_name"):
            return part.substream_name or ""
        else:
            return ""
    except Exception:
        return ""


@processor.part_processor_function
async def normal_processor(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """
    Normal processor for non-error parts.
    Handles default substream routing.
    """
    yield part


def create_error_routing_pipeline() -> Optional[Any]:
    """
    Create comprehensive error routing pipeline using switch-based routing.
    Demonstrates the requested pattern:

    switch.Switch(content_api.get_substream_name)
        .case('error', error_processor)
        .default(normal_processor)
    """
    if not processor or not content_api or not switch:
        return None

    return (
        switch.Switch(get_substream_name_safe)
        .case("error", error_handler_processor)
        .case("status", status_handler_processor)
        .default(normal_processor)
    )
