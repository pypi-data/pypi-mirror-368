#!/usr/bin/env python3
"""
A fully processor-based TDD validation pipeline.
"""

import ast
import json
import os
import re
from typing import AsyncIterable, Dict, Any, Optional

from genai_processors import ProcessorPart

from .file_storage import FileStorage
from .streaming_processors import (
    ValidationProcessor,
    TDDValidationProcessor,
    FileCategorizationProcessor,
    FileCategorizationPromptBuilder,
    TDDPromptBuilder,
    extract_json_from_part,
)


def count_test_functions(code_content: str) -> int:
    """Count test functions in Python code using AST parsing."""
    if not code_content:
        return 0

    try:
        tree = ast.parse(code_content)
        test_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_count += 1

        return test_count
    except SyntaxError:
        # Fallback to regex if AST parsing fails
        return len(re.findall(r"^def test_\w+\s*\(", code_content, re.MULTILINE))


def analyze_test_changes(
    old_content: str, new_content: str, file_path: str, tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze changes to test files and return test change information."""
    if tool_name is None:
        tool_name = "Update" if old_content else "Write"

    # Treat Update on non-existent files like Write operations
    if tool_name == "Update" and not old_content:
        tool_name = "Write"

    if tool_name == "Write":
        # For new files, count total tests
        new_test_count = count_test_functions(new_content)
        if new_test_count > 1:
            return {
                "approved": False,
                "reason": f"TDD: Multiple tests ({new_test_count}) in new file. Only ONE test per operation allowed.",
                "test_count": new_test_count,
                "tdd_phase": "red",
                "suggestions": [
                    "Write only one failing test at a time",
                    "Follow Red-Green-Refactor cycle",
                    "Split into multiple operations if multiple tests needed",
                ],
            }
        elif new_test_count == 1:
            return {
                "approved": True,
                "reason": "TDD RED phase: Single new test allowed.",
                "test_count": new_test_count,
                "tdd_phase": "red",
                "suggestions": [],
            }
        else:
            return {
                "approved": True,
                "reason": "TDD: No tests found in file.",
                "test_count": 0,
                "tdd_phase": "skipped",
                "suggestions": [],
            }

    else:  # Update, Edit, or MultiEdit operation
        old_test_count = count_test_functions(old_content)
        new_test_count = count_test_functions(new_content)
        net_new_tests = new_test_count - old_test_count

        if net_new_tests > 1:
            return {
                "approved": False,
                "reason": f"TDD: Multiple new tests ({net_new_tests}) added. Only ONE test per operation allowed.",
                "test_count": net_new_tests,
                "tdd_phase": "red",
                "suggestions": [
                    "Add only one failing test at a time",
                    "Follow Red-Green-Refactor cycle",
                    "Split into multiple operations if multiple tests needed",
                ],
            }
        elif net_new_tests == 1:
            return {
                "approved": True,
                "reason": "TDD RED phase: Single new test added.",
                "test_count": net_new_tests,
                "tdd_phase": "red",
                "suggestions": [],
            }
        elif net_new_tests == 0:
            return {
                "approved": True,
                "reason": "TDD REFACTOR phase: Test modification without adding new tests.",
                "test_count": net_new_tests,
                "tdd_phase": "refactor",
                "suggestions": [],
            }
        else:  # net_new_tests < 0 (tests removed)
            return {
                "approved": True,
                "reason": f"TDD REFACTOR phase: {abs(net_new_tests)} test(s) removed/refactored.",
                "test_count": net_new_tests,
                "tdd_phase": "refactor",
                "suggestions": [],
            }


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

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)

    def match(self, part: ProcessorPart) -> bool:
        return extract_json_from_part(part).get("heuristic_decision") == "proceed"


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

    def validate(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        # Create simple synchronous processing pipeline
        current_data: Dict[str, Any] = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "context": context,
        }

        # Process step by step without async processor framework

        # Step 1: TDD Relevance Check
        tdd_relevant_operations = ["Write", "Edit", "MultiEdit", "Update"]
        current_data["is_tdd_relevant"] = tool_name in tdd_relevant_operations

        if not current_data["is_tdd_relevant"]:
            return {
                "approved": True,
                "reason": "TDD validation not applicable to this tool operation",
                "tdd_phase": "skipped",
                "suggestions": [],
            }

        # Step 2: Load TDD Context
        from .file_storage import FileStorage

        file_storage = FileStorage()
        current_data["tdd_context"] = file_storage.get_tdd_context()

        # Step 3: Build File Categorization Prompt (if needed)
        tdd_context = current_data.get("tdd_context", {})
        test_results = tdd_context.get("test_results", {})

        # Skip categorization if there are collection errors
        if not (test_results and len(test_results.get("collection_errors", [])) > 0):
            # Build categorization prompt
            file_path = tool_input.get("file_path", "")

            # Get content based on tool type
            if tool_name == "Write":
                content = tool_input.get("content", "")
            elif tool_name == "Edit":
                # For Edit, we need to simulate the edit to get the resulting content
                content = ""
                old_string = tool_input.get("old_string", "")
                new_string = tool_input.get("new_string", "")

                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            original_content = f.read()
                            # Apply the edit operation
                            if old_string in original_content:
                                content = original_content.replace(
                                    old_string, new_string, 1
                                )
                            else:
                                content = original_content
                    except Exception:
                        # If file can't be read, just use the new_string for analysis
                        content = new_string
                else:
                    # If file doesn't exist, treat new_string as the content for analysis
                    content = new_string
            elif tool_name == "MultiEdit":
                # For MultiEdit, apply all edits to generate the new content
                content = ""
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception:
                        pass
                else:
                    # If file doesn't exist, treat all new_strings as new content for analysis
                    edits = tool_input.get("edits", [])
                    content_parts = []
                    for edit in edits:
                        new_string = edit.get("new_string", "")
                        if new_string:
                            content_parts.append(new_string)
                    content = "\n".join(content_parts)

                # Apply all edits sequentially if file exists
                if os.path.exists(file_path):
                    edits = tool_input.get("edits", [])
                    for edit in edits:
                        old_string = edit.get("old_string", "")
                        new_string = edit.get("new_string", "")
                        if old_string and old_string in content:
                            content = content.replace(old_string, new_string, 1)
            else:
                content = tool_input.get("content", "")

            # Simple file categorization without LLM
            # Extract filename from path for pattern matching
            filename = os.path.basename(file_path)
            if (
                file_path.endswith("_test.py")
                or file_path.endswith("test_")
                or filename.startswith("test_")
                or "_test" in filename
                or "test_" in filename
                or "/test_" in file_path
                or "/tests/" in file_path
            ):
                category = "test"
                requires_tdd = True
            elif (
                file_path.endswith("__init__.py")
                or file_path.endswith("setup.py")
                or file_path.endswith("conftest.py")
            ):
                category = "structural"
                requires_tdd = False
            elif file_path.endswith((".py", ".js", ".ts")):
                category = "implementation"
                requires_tdd = True
            elif file_path.endswith(
                (".txt", ".md", ".rst", ".json", ".yaml", ".yml", ".toml", ".ini")
            ):
                category = "config"  # Treat simple text files as config
                requires_tdd = False
            else:
                category = "unknown"
                requires_tdd = False  # Be more permissive for unknown files

            current_data["file_category"] = {
                "category": category,
                "requires_tdd": requires_tdd,
                "reason": "Simple heuristic categorization",
            }

        # Step 4: TDD Heuristic Processing
        has_failing_tests = bool(
            test_results
            and (
                test_results.get("failures")
                or test_results.get("errors", 0) > 0
                or len(test_results.get("collection_errors", [])) > 0
            )
        )

        category_info = current_data.get("file_category", {})
        category = category_info.get("category", "unknown")
        requires_tdd = category_info.get("requires_tdd", True)

        # Check for collection errors (valid Red state)
        if test_results and len(test_results.get("collection_errors", [])) > 0:
            return {
                "approved": True,
                "reason": "TDD GREEN phase: Implementation allowed to fix collection errors.",
                "tdd_phase": "green",
                "suggestions": [],
            }

        # Test files need sophisticated analysis for the "one test at a time" rule
        if category == "test":
            # Get old content for Update, Edit, and MultiEdit operations
            old_content = ""
            if tool_name in ["Update", "Edit", "MultiEdit"] and os.path.exists(
                file_path
            ):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                except Exception:
                    old_content = ""

            # Analyze test changes
            test_analysis = analyze_test_changes(
                old_content, content, file_path, tool_name
            )
            return test_analysis

        # Non-code files and files that don't require TDD are automatically approved
        non_code_categories = ["structural", "config", "docs", "data", "template"]
        if category and (category in non_code_categories or not requires_tdd):
            return {
                "approved": True,
                "reason": f"TDD validation not required for {category} files.",
                "tdd_phase": "skipped",
                "suggestions": [],
            }

        # If we have failing tests, allow implementation
        if has_failing_tests:
            return {
                "approved": True,
                "reason": "TDD GREEN phase: Implementation allowed to fix failing tests.",
                "tdd_phase": "green",
                "suggestions": [],
            }

        # Block implementation if no failing tests and it's categorized as implementation
        if category == "implementation":
            return {
                "approved": False,
                "reason": "TDD: Implementation change without a failing test.",
                "tdd_phase": "refactor",
                "suggestions": [
                    "Add a failing test first (Red phase)",
                    "Ensure tests are running and capturing failures",
                ],
            }

        # Default to requiring deep analysis for unknown cases
        return {
            "approved": False,
            "reason": "TDD: Uncertain validation state - deep analysis would be required.",
            "tdd_phase": "unknown",
            "suggestions": ["Configure GEMINI_API_KEY for deep TDD analysis"],
        }
