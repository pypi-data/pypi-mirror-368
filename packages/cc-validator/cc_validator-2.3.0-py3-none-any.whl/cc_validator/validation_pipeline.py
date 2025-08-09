#!/usr/bin/env python3
"""
Advanced validation pipeline using genai-processors streaming pattern.
Demonstrates chaining processors for complex validation workflows.
"""

import json
from typing import AsyncIterable, Optional, Dict, Any

try:
    from genai_processors import processor, ProcessorPart
except ImportError:
    processor = None
    ProcessorPart = None

from .streaming_processors import (
    SecurityValidationProcessor,
    TDDValidationProcessor,
    FileCategorizationProcessor,
    ValidationProcessor,
    extract_json_from_part,
)


class ContextEnrichmentProcessor(ValidationProcessor):
    """Enriches validation requests with additional context"""

    def __init__(self, context: str):
        super().__init__()
        self.context = context

    def match(self, part: ProcessorPart) -> bool:
        """Match JSON parts with validation requests"""
        json_data = extract_json_from_part(part)
        return "prompt" in json_data

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Enrich the validation request with context"""
        json_data = extract_json_from_part(part)
        if json_data and "prompt" in json_data:
            enriched_request = json_data.copy()
            # Add context to the prompt
            original_prompt = enriched_request.get("prompt", "")
            enriched_request["prompt"] = (
                f"{original_prompt}\n\nCONTEXT:\n{self.context}"
            )

            yield ProcessorPart(json.dumps(enriched_request))
        else:
            yield part


class ValidationResultAggregator(ValidationProcessor):
    """Aggregates results from multiple validation processors"""

    def __init__(self) -> None:
        super().__init__()
        self.results: Dict[str, Any] = {}

    def match(self, part: ProcessorPart) -> bool:
        """Match JSON parts with validation results"""
        json_data = extract_json_from_part(part)
        return bool(json_data)

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Aggregate validation results"""
        json_data = extract_json_from_part(part)
        if json_data:
            # Aggregate results
            self.results.update(json_data)

            # Determine overall approval
            if "approved" in json_data:
                overall_approved = all(
                    self.results.get(key, True)
                    for key in ["approved", "security_approved", "tdd_approved"]
                    if key in self.results
                )
                self.results["overall_approved"] = overall_approved

            yield ProcessorPart(json.dumps(self.results))
        else:
            yield part


class ValidationStatusProcessor(ValidationProcessor):
    """Adds status messages to the validation pipeline"""

    def __init__(self, status_message: str):
        super().__init__()
        self.status_message = status_message

    def match(self, part: ProcessorPart) -> bool:
        """Always match to add status"""
        return True

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Add status to the stream"""
        # First yield the original part
        yield part

        # Then yield status as a ProcessorPart with status field
        status_part = ProcessorPart(json.dumps({"status": self.status_message}))
        yield status_part


class HybridValidationPipeline:
    """Advanced validation pipeline using processor composition"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

        # Create individual processors
        self.security_processor = SecurityValidationProcessor(api_key)
        self.tdd_processor = TDDValidationProcessor(api_key)
        self.file_categorizer = FileCategorizationProcessor(api_key)

    def create_file_validation_pipeline(self, context: str) -> Any:
        """Create a pipeline for file validation"""
        # Chain processors: enrich → categorize → validate → aggregate → status
        pipeline = (
            ContextEnrichmentProcessor(context)
            + self.file_categorizer
            + ValidationStatusProcessor("File categorized")
            + self.security_processor
            + ValidationStatusProcessor("Security validated")
            + self.tdd_processor
            + ValidationStatusProcessor("TDD validated")
            + ValidationResultAggregator()
            + ValidationStatusProcessor("Validation complete!")
        )
        return pipeline

    def create_security_only_pipeline(self, context: str) -> Any:
        """Create a pipeline for security-only validation"""
        pipeline = (
            ContextEnrichmentProcessor(context)
            + self.security_processor
            + ValidationStatusProcessor("Security validation complete!")
        )
        return pipeline

    def validate_file_operation(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """Validate a file operation through the complete pipeline"""
        # Create initial validation request
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        validation_request = {
            "tool_name": tool_name,
            "file_path": file_path,
            "content": content,
            "prompt": f"Validate {tool_name} operation on {file_path}",
        }

        # Create input parts
        input_parts = [ProcessorPart(json.dumps(validation_request))]

        # Create and run pipeline
        pipeline = self.create_file_validation_pipeline(context)

        # Collect results using synchronous execution
        final_result = {}
        processed_parts = processor.apply_sync(pipeline, input_parts)
        for part in processed_parts:
            json_data = extract_json_from_part(part)
            if json_data:
                if "status" in json_data:
                    print(f"Pipeline status: {json_data['status']}")
                else:
                    final_result.update(json_data)

        return final_result


class OperationValidationProcessor(ValidationProcessor):
    """Processor wrapper for individual validation operations"""

    def __init__(
        self,
        hybrid_pipeline: "HybridValidationPipeline",
        tool_name: str,
        tool_input: Dict[str, Any],
        context: str,
        operation_index: int,
    ):
        super().__init__()
        self.hybrid_pipeline = hybrid_pipeline
        self.tool_name = tool_name
        self.tool_input = tool_input
        self.context = context
        self.operation_index = operation_index

    def match(self, part: ProcessorPart) -> bool:
        """Always match - this processor handles its own specific operation"""
        return True

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Execute the validation operation and yield the result"""
        try:
            result = self.hybrid_pipeline.validate_file_operation(
                self.tool_name, self.tool_input, self.context
            )
            # Add operation index to track results
            result["operation_index"] = self.operation_index
            yield ProcessorPart(json.dumps(result))
        except Exception as e:
            # Handle exceptions gracefully
            error_result = {
                "error": str(e),
                "operation": {
                    "tool_name": self.tool_name,
                    "tool_input": self.tool_input,
                },
                "approved": False,
                "operation_index": self.operation_index,
            }
            yield ProcessorPart(json.dumps(error_result))


class ParallelValidationPipeline:
    """Run multiple validation pipelines in parallel using genai-processors"""

    def __init__(self, api_key: Optional[str] = None):
        self.hybrid_pipeline = HybridValidationPipeline(api_key)
        self.api_key = api_key

    def validate_parallel(
        self, operations: list[Dict[str, Any]], context: str
    ) -> list[Dict[str, Any]]:
        """Validate multiple operations in parallel using processor.parallel_concat()"""

        if not processor or not operations:
            # Fallback or empty case
            return self._fallback_parallel_validation(operations, context)

        # Create individual validation processors for each operation
        validation_processors = []
        for i, op in enumerate(operations):
            operation_processor = OperationValidationProcessor(
                self.hybrid_pipeline, op["tool_name"], op["tool_input"], context, i
            )
            validation_processors.append(operation_processor)

        # Create parallel processor
        parallel_processor = processor.parallel_concat(validation_processors)

        # Create input parts (empty input since processors have their own inputs)
        input_parts = [ProcessorPart("{}")]

        # Collect results using synchronous execution
        results_by_index = {}
        processed_parts = processor.apply_sync(parallel_processor, input_parts)
        for result_part in processed_parts:
            result_data = extract_json_from_part(result_part)
            if result_data and "operation_index" in result_data:
                index = result_data["operation_index"]
                # Remove the operation_index from the final result
                clean_result = {
                    k: v for k, v in result_data.items() if k != "operation_index"
                }
                results_by_index[index] = clean_result

        # Build final results list in original order
        final_results: list[Dict[str, Any]] = []
        for i, op in enumerate(operations):
            if i in results_by_index:
                final_results.append(results_by_index[i])
            else:
                # Fallback result if operation failed or didn't complete
                final_results.append(
                    {
                        "error": "Operation validation did not complete",
                        "operation": op,
                        "approved": False,
                    }
                )

        return final_results

    def _fallback_parallel_validation(
        self, operations: list[Dict[str, Any]], context: str
    ) -> list[Dict[str, Any]]:
        """Fallback processing when genai_processors is not available"""
        final_results: list[Dict[str, Any]] = []

        # Process operations sequentially since this is fallback code
        for i, op in enumerate(operations):
            try:
                result = self.hybrid_pipeline.validate_file_operation(
                    op["tool_name"], op["tool_input"], context
                )
                final_results.append(result)
            except Exception as e:
                final_results.append(
                    {
                        "error": str(e),
                        "operation": op,
                        "approved": False,  # Deny on error
                    }
                )

        return final_results
