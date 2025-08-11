#!/usr/bin/env python3
"""
Canonical PartProcessor implementations for SecurityValidation and TDD validation.
Following 100% genai-processors canonical patterns from official examples.

Usage Example:
    # Security validation processor
    security_processor = SecurityValidationProcessor()

    # TDD validation processor
    tdd_processor = TDDValidationProcessor()

    # Generic validation processor with custom function
    def custom_validator(tool_name, tool_input):
        return {"approved": True, "reason": "Custom validation"}

    generic_processor = GenericValidationProcessor(custom_validator)

    # Use with genai-processors pipeline composition
    pipeline = security_processor + tdd_processor

    # Process parts
    async for result in pipeline(input_stream):
        result_data = result.get_dataclass(SecurityResult) or result.get_dataclass(TDDResult)
        print(f"Approved: {result_data.approved}, Reason: {result_data.reason}")
"""

from typing import AsyncIterable, Dict, Any, Optional

try:
    from genai_processors import processor, content_api
except ImportError:
    processor = None
    content_api = None

from .file_storage import FileStorage
from .validation_dataclasses import (
    ToolInputData,
    SecurityResult,
    TDDResult,
    ProcessorResult,
    create_part_from_dataclass,
)
from .validation_logic import (
    validate_security_pure,
    validate_tdd_pure,
    _extract_tool_input_data_safe,
)


class SecurityValidationProcessor(processor.PartProcessor):
    """Security validation processor following canonical genai-processors patterns."""

    def __init__(self, config: Optional[Any] = None) -> None:
        """Initialize security validation processor."""
        self.config = config

    def match(self, part: processor.ProcessorPart) -> bool:
        """Only process ToolInputData parts."""
        if not content_api:
            return False
        return content_api.is_dataclass(part.mimetype, ToolInputData)  # type: ignore[no-any-return]

    async def call(
        self, part: processor.ProcessorPart
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Process security validation using canonical patterns - compatible with pipeline."""
        try:
            tool_input_data = _extract_tool_input_data_safe(part)
            if not tool_input_data:
                yield part
                return

            tool_name = tool_input_data.tool_name
            tool_input = tool_input_data.tool_input

            # Handle TodoWrite optimization
            if tool_name == "TodoWrite":
                file_storage = FileStorage()
                todos = tool_input.get("todos", [])
                file_storage.store_todo_state({"todos": todos})

                # Create early exit response for TodoWrite preserving ToolInputData structure

                # Create a new ToolInputData with early exit info in storage_context
                updated_tool_data = ToolInputData(
                    tool_name=tool_input_data.tool_name,
                    tool_input=tool_input_data.tool_input,
                    context=tool_input_data.context,
                    api_key=tool_input_data.api_key,
                    pipeline_initialized=tool_input_data.pipeline_initialized,
                    storage_context={
                        **tool_input_data.storage_context,
                        "_early_exit": True,
                        "security_approved": True,
                        "final_security_result": {
                            "approved": True,
                            "reason": "TodoWrite operations skip security validation",
                            "suggestions": [],
                        },
                    },
                )

                result_part = create_part_from_dataclass(updated_tool_data)
                if result_part:
                    yield result_part
                else:
                    # Fallback to JSON if dataclass creation fails
                    data = self._get_json_data_safe(part)
                    data.update(
                        {
                            "tool_name": tool_input_data.tool_name,
                            "tool_input": tool_input_data.tool_input,
                            "context": tool_input_data.context,
                            "api_key": tool_input_data.api_key,
                            "pipeline_initialized": tool_input_data.pipeline_initialized,
                            "storage_context": tool_input_data.storage_context,
                            "_early_exit": True,
                            "security_approved": True,
                            "final_security_result": {
                                "approved": True,
                                "reason": "TodoWrite operations skip security validation",
                                "suggestions": [],
                            },
                        }
                    )
                    # Create SecurityResult for fallback case
                    security_result = SecurityResult(
                        approved=True,
                        reason="TodoWrite operations skip security validation",
                        severity="none",
                        suggestions=[],
                    )
                    result_part = create_part_from_dataclass(security_result)
                    if result_part:
                        yield result_part
                return

            # Perform security validation
            security_result_dict = validate_security_pure(tool_name, tool_input)

            # Create response with security result in pipeline format
            data = self._get_json_data_safe(part)
            data["final_security_result"] = {
                "approved": security_result_dict["approved"],
                "reason": security_result_dict["reason"],
                "suggestions": security_result_dict.get("suggestions", []),
                "severity": security_result_dict.get("severity", "medium"),
            }
            data["security_approved"] = security_result_dict["approved"]

            # Create SecurityResult dataclass
            sec_result = SecurityResult(
                approved=security_result_dict["approved"],
                reason=security_result_dict["reason"],
                severity=security_result_dict.get("severity", "medium"),
                suggestions=security_result_dict.get("suggestions", []),
            )
            result_part = create_part_from_dataclass(sec_result)
            if result_part:
                yield result_part

        except Exception as e:
            from .processor_factories import create_processor_error_part

            error_part = create_processor_error_part(
                error_message=f"Security validation processor failed: {str(e)}",
                error_type="SecurityValidationProcessorError",
                processor_name="security_validation_processor",
                error_code="SEC001",
                severity="critical",
                suggestions=[
                    "Check security processor configuration",
                    "Verify input data format",
                ],
            )
            if hasattr(error_part, "substream_name"):
                error_part.substream_name = "error"
            elif hasattr(content_api, "set_substream_name"):
                content_api.set_substream_name(error_part, "error")
            yield error_part

    def _get_json_data_safe(self, part: content_api.ProcessorPart) -> Dict[str, Any]:
        """Safe JSON data extraction with fallback"""
        try:
            if hasattr(part, "json") and part.json:
                return dict(part.json)
            elif hasattr(part, "text") and part.text:
                import json

                return json.loads(part.text)  # type: ignore[no-any-return]
            return {}
        except (ImportError, Exception):
            return {}


class TDDValidationProcessor(processor.PartProcessor):
    """TDD validation processor following canonical genai-processors patterns."""

    def __init__(self, config: Optional[Any] = None) -> None:
        """Initialize TDD validation processor."""
        self.config = config
        self.file_storage = FileStorage()

    def match(self, part: processor.ProcessorPart) -> bool:
        """Only process ToolInputData parts."""
        if not content_api:
            return False
        return content_api.is_dataclass(part.mimetype, ToolInputData)  # type: ignore[no-any-return]

    async def call(
        self, part: processor.ProcessorPart
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Process TDD validation using canonical patterns - compatible with pipeline."""
        try:
            tool_input_data = _extract_tool_input_data_safe(part)
            if not tool_input_data:
                yield part
                return

            tool_name = tool_input_data.tool_name
            tool_input = tool_input_data.tool_input

            # Handle TodoWrite optimization
            if tool_name == "TodoWrite":
                # Create early exit response for TodoWrite preserving ToolInputData structure

                # Create a new ToolInputData with early exit info in storage_context
                updated_tool_data = ToolInputData(
                    tool_name=tool_input_data.tool_name,
                    tool_input=tool_input_data.tool_input,
                    context=tool_input_data.context,
                    api_key=tool_input_data.api_key,
                    pipeline_initialized=tool_input_data.pipeline_initialized,
                    storage_context={
                        **tool_input_data.storage_context,
                        "_early_exit": True,
                        "tdd_approved": True,
                        "final_tdd_result": {
                            "approved": True,
                            "reason": "TodoWrite operations skip TDD validation",
                            "suggestions": [],
                            "tdd_phase": "skipped",
                        },
                    },
                )

                result_part = create_part_from_dataclass(updated_tool_data)
                if result_part:
                    yield result_part
                else:
                    # Fallback to JSON if dataclass creation fails
                    data = self._get_json_data_safe(part)
                    data.update(
                        {
                            "tool_name": tool_input_data.tool_name,
                            "tool_input": tool_input_data.tool_input,
                            "context": tool_input_data.context,
                            "api_key": tool_input_data.api_key,
                            "pipeline_initialized": tool_input_data.pipeline_initialized,
                            "storage_context": tool_input_data.storage_context,
                            "_early_exit": True,
                            "tdd_approved": True,
                            "final_tdd_result": {
                                "approved": True,
                                "reason": "TodoWrite operations skip TDD validation",
                                "suggestions": [],
                                "tdd_phase": "skipped",
                            },
                        }
                    )
                    # Create TDDResult for fallback case
                    tdd_result = TDDResult(
                        approved=True,
                        reason="TodoWrite operations skip TDD validation",
                        tdd_phase="skipped",
                        suggestions=[],
                    )
                    result_part = create_part_from_dataclass(tdd_result)
                    if result_part:
                        yield result_part
                return

            # Get TDD context from storage
            tdd_context = self.file_storage.get_tdd_context()

            # Perform TDD validation
            tdd_result_dict = validate_tdd_pure(tool_name, tool_input, tdd_context)

            # Create response with TDD result in pipeline format
            data = self._get_json_data_safe(part)
            data["final_tdd_result"] = {
                "approved": tdd_result_dict["approved"],
                "reason": tdd_result_dict["reason"],
                "suggestions": tdd_result_dict.get("suggestions", []),
                "tdd_phase": tdd_result_dict.get("tdd_phase", "unknown"),
            }
            data["tdd_approved"] = tdd_result_dict["approved"]

            # Add TDD-specific fields when available
            if "test_count" in tdd_result_dict:
                data["final_tdd_result"]["test_count"] = tdd_result_dict["test_count"]
                data["test_count"] = tdd_result_dict["test_count"]
            if "tdd_phase" in tdd_result_dict:
                data["tdd_phase"] = tdd_result_dict["tdd_phase"]

            # Create TDDResult dataclass
            tdd_res = TDDResult(
                approved=tdd_result_dict["approved"],
                reason=tdd_result_dict["reason"],
                tdd_phase=tdd_result_dict.get("tdd_phase", "unknown"),
                test_count=tdd_result_dict.get("test_count"),
                suggestions=tdd_result_dict.get("suggestions", []),
            )
            result_part = create_part_from_dataclass(tdd_res)
            if result_part:
                yield result_part

        except Exception as e:
            from .processor_factories import create_processor_error_part

            error_part = create_processor_error_part(
                error_message=f"TDD validation processor failed: {str(e)}",
                error_type="TDDValidationProcessorError",
                processor_name="tdd_validation_processor",
                error_code="TDD001",
                severity="critical",
                suggestions=[
                    "Check TDD processor configuration",
                    "Verify test context availability",
                ],
            )
            if hasattr(error_part, "substream_name"):
                error_part.substream_name = "error"
            elif hasattr(content_api, "set_substream_name"):
                content_api.set_substream_name(error_part, "error")
            yield error_part

    def _get_json_data_safe(self, part: content_api.ProcessorPart) -> Dict[str, Any]:
        """Safe JSON data extraction with fallback"""
        try:
            if hasattr(part, "json") and part.json:
                return dict(part.json)
            elif hasattr(part, "text") and part.text:
                import json

                return json.loads(part.text)  # type: ignore[no-any-return]
            return {}
        except (ImportError, Exception):
            return {}


class GenericValidationProcessor(processor.PartProcessor):
    """Generic validation processor for extensible validation logic."""

    def __init__(
        self,
        validation_func: Any,
        result_type: Any = ProcessorResult,
        config: Optional[Any] = None,
    ) -> None:
        """Initialize with validation function and result type."""
        self.validation_func = validation_func
        self.result_type = result_type
        self.config = config

    def match(self, part: processor.ProcessorPart) -> bool:
        """Only process ToolInputData parts."""
        if not content_api:
            return False
        return content_api.is_dataclass(part.mimetype, ToolInputData)  # type: ignore[no-any-return]

    async def call(
        self, part: processor.ProcessorPart
    ) -> AsyncIterable[processor.ProcessorPart]:
        """Process validation using provided function."""
        if not self.match(part):
            yield part
            return

        tool_data = part.get_dataclass(ToolInputData)

        validation_result = self.validation_func(
            tool_data.tool_name, tool_data.tool_input
        )

        if self.result_type == ProcessorResult:
            result = ProcessorResult(
                approved=validation_result["approved"],
                reason=validation_result["reason"],
                processor_type="generic",
                severity=validation_result.get("severity", "none"),
                suggestions=validation_result.get("suggestions", []),
                metadata=validation_result.get("metadata", {}),
            )
        else:
            result = self.result_type(**validation_result)

        result_part = create_part_from_dataclass(result)
        if result_part:
            yield result_part
        else:
            yield processor.ProcessorPart.from_dataclass(dataclass=result)
