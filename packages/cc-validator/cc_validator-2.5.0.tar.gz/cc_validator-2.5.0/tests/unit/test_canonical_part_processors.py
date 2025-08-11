#!/usr/bin/env python3
"""
Tests for canonical function-based processors to verify 100% genai-processors compliance.
Tests the canonical @processor.part_processor_function implementations.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch

try:
    from genai_processors import content_api, processor, streams
except ImportError:
    content_api = None
    processor = None
    streams = None

# Removed imports from deleted streaming_processors module
# These processors are now part of validation_logic
from cc_validator.canonical_pipeline import (
    create_canonical_validation_pipeline,
)
from cc_validator.validation_logic import (
    unified_security_tdd_processor,
    validate_security_pure,
    validate_tdd_pure,
)
from cc_validator.canonical_processors import (
    SecurityValidationProcessor,
    TDDValidationProcessor,
    GenericValidationProcessor,
)
from cc_validator.validation_dataclasses import (
    ValidationRequest,
    SecurityValidationResult,
    TDDValidationResult,
    ToolInputData,
    SecurityResult,
    TDDResult,
)


@pytest.fixture
def mock_validation_request():
    """Create mock ValidationRequest data."""
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": "/test/file.py", "content": "def test(): pass"},
        "context": "Test operation",
        "api_key": "test-key",
        "_processor_type": "security",
    }


@pytest.fixture
def mock_tdd_validation_request():
    """Create mock TDD ValidationRequest data."""
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": "/test/file.py", "content": "def test(): pass"},
        "context": "Test operation",
        "api_key": "test-key",
        "_processor_type": "tdd",
    }


class TestUnifiedSecurityTDDProcessor:
    """Test unified_security_tdd_processor 100% native implementation."""

    @pytest.mark.asyncio
    async def test_unified_processor_with_todowrite(self):
        """Test unified processor with TodoWrite operation."""
        if not content_api:
            pytest.skip("genai-processors not available")

        data = {
            "tool_name": "TodoWrite",
            "tool_input": {"todos": [{"content": "test", "status": "pending"}]},
            "context": "test",
        }

        part = content_api.ProcessorPart(json.dumps(data))

        results = []
        async for result in unified_security_tdd_processor(part):
            results.append(result)

        assert len(results) == 1
        result_data = json.loads(results[0].text)
        assert result_data["approved"] is True
        assert "TodoWrite" in result_data["reason"]

    @pytest.mark.asyncio
    async def test_unified_processor_with_write_operation(self):
        """Test unified processor with Write operation."""
        if not content_api:
            pytest.skip("genai-processors not available")

        data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/test/file.py", "content": "print('hello')"},
            "context": "test",
            "api_key": "mock-key",
        }

        with (
            patch(
                "cc_validator.validation_logic.validate_security_pure"
            ) as mock_security,
            patch("cc_validator.validation_logic.validate_tdd_pure") as mock_tdd,
        ):

            mock_security.return_value = {
                "approved": True,
                "reason": "Security passed",
                "suggestions": [],
            }
            mock_tdd.return_value = {
                "approved": True,
                "reason": "TDD passed",
                "suggestions": [],
                "tdd_phase": "green",
            }

            part = content_api.ProcessorPart(json.dumps(data))

            results = []
            async for result in unified_security_tdd_processor(part):
                results.append(result)

            assert len(results) == 1
            result_data = json.loads(results[0].text)
            assert result_data["approved"] is True
            mock_security.assert_called_once()
            mock_tdd.assert_called_once()


class TestPureFunctions:
    """Test pure validation functions."""

    def test_validate_security_pure_with_bash(self):
        """Test pure security validation with Bash tool."""
        result = validate_security_pure("Bash", {"command": "echo hello"})

        assert "approved" in result
        assert "reason" in result
        assert isinstance(result["approved"], bool)

    def test_validate_security_pure_with_dangerous_command(self):
        """Test pure security validation with dangerous command."""
        result = validate_security_pure("Bash", {"command": "rm -rf /"})

        assert result["approved"] is False
        assert "dangerous" in result["reason"].lower()

    def test_validate_tdd_pure_with_non_relevant_tool(self):
        """Test pure TDD validation with non-relevant tool."""
        result = validate_tdd_pure("Bash", {"command": "echo hello"}, {})

        assert result["approved"] is True
        assert "not applicable" in result["reason"]
        assert result["tdd_phase"] == "skipped"


class TestPipelineCreation:
    """Test canonical pipeline creation functions."""

    def test_create_canonical_validation_pipeline(self):
        """Test creating canonical validation pipeline."""
        pipeline = create_canonical_validation_pipeline()

        if processor:
            assert pipeline is not None
        else:
            assert pipeline is None


class TestGenericValidationProcessor:
    """Test GenericValidationProcessor for extensibility."""

    @pytest.fixture
    def simple_validation_func(self):
        """Simple validation function for testing."""

        def validate(tool_name, tool_input):
            return {
                "approved": tool_name != "ForbiddenTool",
                "reason": f"Tool {tool_name} validation result",
                "suggestions": (
                    ["Use allowed tools only"] if tool_name == "ForbiddenTool" else []
                ),
            }

        return validate

    @pytest.fixture
    def generic_processor(self, simple_validation_func):
        """Create GenericValidationProcessor instance."""
        return GenericValidationProcessor(simple_validation_func)

    def test_match_with_tool_input_data(self, generic_processor):
        """Test match method with ToolInputData part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        tool_data = ToolInputData(
            tool_name="Write",
            tool_input={"file_path": "/test/file.py", "content": "print('hello')"},
            context="Test operation",
        )

        part = content_api.ProcessorPart.from_dataclass(dataclass=tool_data)
        result = generic_processor.match(part)

        assert result is True

    @pytest.mark.asyncio
    async def test_call_with_allowed_tool(self, generic_processor):
        """Test call method with allowed tool."""
        if not content_api:
            pytest.skip("genai-processors not available")

        tool_data = ToolInputData(
            tool_name="Write",
            tool_input={"file_path": "/test/file.py", "content": "print('hello')"},
            context="Test operation",
        )

        part = content_api.ProcessorPart.from_dataclass(dataclass=tool_data)

        results = []
        async for result in generic_processor.call(part):
            results.append(result)

        assert len(results) == 1
        from cc_validator.validation_dataclasses import ProcessorResult

        processor_result = results[0].get_dataclass(ProcessorResult)
        assert processor_result is not None
        assert processor_result.approved is True
        assert "Write" in processor_result.reason

    @pytest.mark.asyncio
    async def test_call_with_forbidden_tool(self, generic_processor):
        """Test call method with forbidden tool."""
        if not content_api:
            pytest.skip("genai-processors not available")

        tool_data = ToolInputData(
            tool_name="ForbiddenTool",
            tool_input={"some": "input"},
            context="Test operation",
        )

        part = content_api.ProcessorPart.from_dataclass(dataclass=tool_data)

        results = []
        async for result in generic_processor.call(part):
            results.append(result)

        assert len(results) == 1
        from cc_validator.validation_dataclasses import ProcessorResult

        processor_result = results[0].get_dataclass(ProcessorResult)
        assert processor_result is not None
        assert processor_result.approved is False
        assert len(processor_result.suggestions) == 1
