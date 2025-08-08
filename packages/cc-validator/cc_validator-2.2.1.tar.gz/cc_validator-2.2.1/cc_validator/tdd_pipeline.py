#!/usr/bin/env python3
"""
A fully processor-based TDD validation pipeline.
"""

import json
from typing import AsyncIterable, Dict, Any, Optional

from genai_processors import ProcessorPart, streams

from .file_storage import FileStorage
from .streaming_processors import (
    ValidationProcessor,
    TDDValidationProcessor,
    FileCategorizationProcessor,
    FileCategorizationPromptBuilder,
    TDDPromptBuilder,
    extract_json_from_part,
)


class TDDRelevanceCheckProcessor(ValidationProcessor):
    """Checks if the tool operation is relevant for TDD validation."""

    def match(self, part: ProcessorPart) -> bool:
        return "tool_name" in extract_json_from_part(part)

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        data = extract_json_from_part(part)
        tool_name = data.get("tool_name", "")
        tdd_relevant_operations = ["Write", "Edit", "MultiEdit", "Update"]
        data["is_tdd_relevant"] = tool_name in tdd_relevant_operations
        yield ProcessorPart(json.dumps(data))


class ContextLoadingProcessor(ValidationProcessor):
    """Loads TDD context from file storage."""

    def __init__(self) -> None:
        super().__init__()
        self.file_storage = FileStorage()

    def match(self, part: ProcessorPart) -> bool:
        return bool(extract_json_from_part(part).get("is_tdd_relevant", False))

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        data = extract_json_from_part(part)
        data["tdd_context"] = self.file_storage.get_tdd_context()
        yield ProcessorPart(json.dumps(data))


class TDDHeuristicProcessor(ValidationProcessor):
    """
    Performs fast, rule-based TDD checks.
    """

    def match(self, part: ProcessorPart) -> bool:
        # This processor runs after context loading, file categorization optional
        data = extract_json_from_part(part)
        return data.get("is_tdd_relevant", False) and "tdd_context" in data

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        data = extract_json_from_part(part)

        # If not relevant to TDD, approve immediately
        if not data.get("is_tdd_relevant"):
            data["approved"] = True
            data["reason"] = "TDD validation not applicable to this tool operation"
            data["tdd_phase"] = "skipped"
            yield ProcessorPart(json.dumps(data))
            return

        # Get TDD context FIRST
        tdd_context = data.get("tdd_context", {})
        test_results = tdd_context.get("test_results", {})

        # Check for collection errors BEFORE file categorization. This is a valid "Red" state.
        if test_results and len(test_results.get("collection_errors", [])) > 0:
            data["heuristic_decision"] = (
                "approve"  # Approve implementation to fix collection errors
            )
            data["reason"] = (
                "TDD GREEN phase: Implementation allowed to fix collection errors."
            )
            data["approved"] = True
            data["tdd_phase"] = "green"
            yield ProcessorPart(json.dumps(data))
            return

        category_info = data.get("file_category", {})
        category = category_info.get("category")

        # Test files need deep analysis to enforce the "one test at a time" rule
        if category == "test":
            data["heuristic_decision"] = "proceed"
            yield ProcessorPart(json.dumps(data))
            return

        # If file categorization is available, approve operations on explicitly non-code files only.
        # Unknown files should proceed to deep analysis to be safe.
        non_code_categories = ["structural", "config", "docs", "data", "template"]
        if category and category in non_code_categories:
            data["heuristic_decision"] = "approve"
            data["reason"] = f"TDD validation not required for {category} files."
            data["approved"] = True
            data["tdd_phase"] = "skipped"
            yield ProcessorPart(json.dumps(data))
            return

        # Check for other failing tests.
        has_failing_tests = bool(
            test_results
            and (
                test_results.get("failures")
                or test_results.get("errors", 0) > 0
                or len(test_results.get("collection_errors", [])) > 0
            )
        )

        # If we have failing tests (including collection errors), allow implementation
        if has_failing_tests:
            data["heuristic_decision"] = "approve"
            data["reason"] = (
                "TDD GREEN phase: Implementation allowed to fix failing tests."
            )
            data["approved"] = True
            data["tdd_phase"] = "green"
            yield ProcessorPart(json.dumps(data))
            return

        # Block implementation if there are no failing tests and it's categorized as implementation
        if category == "implementation":
            data["heuristic_decision"] = "block"
            data["reason"] = "TDD: Implementation change without a failing test."
            data["approved"] = False
            data["tdd_phase"] = "refactor"
            yield ProcessorPart(json.dumps(data))
            return

        # If all checks pass, proceed to the deep analysis.
        data["heuristic_decision"] = "proceed"
        yield ProcessorPart(json.dumps(data))


class TDDDeepAnalysisProcessor(TDDValidationProcessor):
    """The final LLM-based TDD analysis."""

    def match(self, part: ProcessorPart) -> bool:
        return extract_json_from_part(part).get("heuristic_decision") == "proceed"

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        # This will call the original TDDValidationProcessor logic
        async for result_part in super().call(part):
            yield result_part


class TDDValidationPipeline:
    def __init__(self, api_key: Optional[str] = None):
        self.pipeline = (
            TDDRelevanceCheckProcessor()
            + ContextLoadingProcessor()
            + FileCategorizationPromptBuilder()
            + FileCategorizationProcessor(api_key)
            + TDDHeuristicProcessor()
            + TDDPromptBuilder()
            + TDDDeepAnalysisProcessor(api_key)
        )

    async def validate(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        initial_data = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "context": context,
        }
        input_stream = streams.stream_content([ProcessorPart(json.dumps(initial_data))])

        final_result = {}
        async for part in self.pipeline(input_stream):
            final_result.update(extract_json_from_part(part))

        # Fallback for non-TDD-relevant operations or empty results
        if not final_result.get("approved") and tool_name not in [
            "Write",
            "Edit",
            "MultiEdit",
            "Update",
        ]:
            return {
                "approved": True,
                "reason": "TDD validation not applicable to this tool operation",
                "tdd_phase": "skipped",
                "suggestions": [],
            }

        return final_result
