#!/usr/bin/env python3
"""
Advanced validation pipeline using genai-processors streaming pattern.
Demonstrates chaining processors for complex validation workflows.
"""

import asyncio
import json
from typing import AsyncIterable, Optional, Dict, Any

try:
    from genai_processors import processor, ProcessorPart, streams
except ImportError:
    processor = None
    ProcessorPart = None
    streams = None

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

    async def validate_file_operation(
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

        # Create input stream
        input_stream = streams.stream_content(
            [ProcessorPart(json.dumps(validation_request))]
        )

        # Create and run pipeline
        pipeline = self.create_file_validation_pipeline(context)

        # Collect results
        final_result = {}
        async for part in pipeline(input_stream):
            json_data = extract_json_from_part(part)
            if json_data:
                if "status" in json_data:
                    print(f"Pipeline status: {json_data['status']}")
                else:
                    final_result.update(json_data)

        return final_result


class ParallelValidationPipeline:
    """Run multiple validation pipelines in parallel"""

    def __init__(self, api_key: Optional[str] = None):
        self.hybrid_pipeline = HybridValidationPipeline(api_key)

    async def validate_parallel(
        self, operations: list[Dict[str, Any]], context: str
    ) -> list[Dict[str, Any]]:
        """Validate multiple operations in parallel"""
        tasks = []

        for op in operations:
            task = self.hybrid_pipeline.validate_file_operation(
                op["tool_name"], op["tool_input"], context
            )
            tasks.append(task)

        # Run all validations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results: list[Dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    {
                        "error": str(result),
                        "operation": operations[i],
                        "approved": False,  # Deny on error
                    }
                )
            else:
                final_results.append(result)  # type: ignore[arg-type]

        return final_results
