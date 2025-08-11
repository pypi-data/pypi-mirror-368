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


class TestSecurityValidationProcessor:
    """Test security validation using unified processor."""

    @pytest.mark.asyncio
    async def test_unified_processor_with_non_matching_part(self):
        """Test unified processor with non-ValidationRequest part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        # Create part with incorrect MIME type
        part = content_api.ProcessorPart("non-json text")

        results = []
        async for result in unified_security_tdd_processor(part):
            results.append(result)

        # Should pass through non-matching parts unchanged
        assert len(results) == 1
        assert results[0].text == "non-json text"

    @pytest.mark.asyncio
    async def test_unified_processor_with_security_validation(
        self, mock_validation_request
    ):
        """Test unified processor security validation behavior."""
        if not content_api:
            pytest.skip("genai-processors not available")

        request_data = dict(mock_validation_request)
        request_data["api_key"] = None

        # Test with a ValidationRequest-like JSON part
        json_part = content_api.ProcessorPart(json.dumps(request_data))

        results = []
        async for result in unified_security_tdd_processor(json_part):
            results.append(result)

        # Should produce at least one result
        assert len(results) >= 1

        # Handle both dataclass and JSON text results
        result_data = None

        # Try each result part to find the main validation result (not error substream)
        for result_part in results:
            # Skip error substream parts
            if (
                hasattr(result_part, "substream_name")
                and result_part.substream_name == "error"
            ):
                continue

            # First try to get dataclass
            if hasattr(result_part, "get_dataclass"):
                from cc_validator.validation_dataclasses import ValidationResponse

                try:
                    validation_response = result_part.get_dataclass(ValidationResponse)
                    if validation_response:
                        result_data = {
                            "approved": validation_response.approved,
                            "reason": validation_response.reason,
                            "suggestions": validation_response.suggestions,
                        }
                        break
                except ValueError:
                    # Not a dataclass part, try JSON text
                    pass

            # If no dataclass, try JSON text
            if (
                result_data is None
                and hasattr(result_part, "text")
                and result_part.text
            ):
                try:
                    result_data = json.loads(result_part.text)
                    if "approved" in result_data:
                        break
                except json.JSONDecodeError:
                    continue

        # Verify we got valid result data
        assert (
            result_data is not None
        ), f"No valid result data found. Results: {[(type(r), getattr(r, 'text', 'N/A'), getattr(r, 'substream_name', None)) for r in results]}"
        assert "approved" in result_data


class TestTDDValidationProcessor:
    """Test TDD validation using unified processor."""

    @pytest.mark.asyncio
    async def test_unified_processor_with_tdd_validation(self):
        """Test unified processor TDD validation behavior."""
        if not content_api:
            pytest.skip("genai-processors not available")

        # Create part with incorrect MIME type
        part = content_api.ProcessorPart("non-json text")

        results = []
        async for result in unified_security_tdd_processor(part):
            results.append(result)

        # Should pass through non-matching parts unchanged
        assert len(results) == 1
        assert results[0].text == "non-json text"

    @pytest.mark.asyncio
    async def test_unified_processor_with_tdd_request(
        self, mock_tdd_validation_request
    ):
        """Test unified processor TDD validation behavior."""
        if not content_api:
            pytest.skip("genai-processors not available")

        request_data = dict(mock_tdd_validation_request)
        request_data["api_key"] = None

        # Test with a ValidationRequest-like JSON part
        json_part = content_api.ProcessorPart(json.dumps(request_data))

        results = []
        async for result in unified_security_tdd_processor(json_part):
            results.append(result)

        # Should produce at least one result
        assert len(results) >= 1

        # Handle both dataclass and JSON text results
        result_data = None

        # Try each result part to find the main validation result (not error substream)
        for result_part in results:
            # Skip error substream parts
            if (
                hasattr(result_part, "substream_name")
                and result_part.substream_name == "error"
            ):
                continue

            # First try to get dataclass
            if hasattr(result_part, "get_dataclass"):
                from cc_validator.validation_dataclasses import ValidationResponse

                try:
                    validation_response = result_part.get_dataclass(ValidationResponse)
                    if validation_response:
                        result_data = {
                            "approved": validation_response.approved,
                            "reason": validation_response.reason,
                            "suggestions": validation_response.suggestions,
                        }
                        break
                except ValueError:
                    # Not a dataclass part, try JSON text
                    pass

            # If no dataclass, try JSON text
            if (
                result_data is None
                and hasattr(result_part, "text")
                and result_part.text
            ):
                try:
                    result_data = json.loads(result_part.text)
                    if "approved" in result_data:
                        break
                except json.JSONDecodeError:
                    continue

        # Verify we got valid result data
        assert (
            result_data is not None
        ), f"No valid result data found. Results: {[(type(r), getattr(r, 'text', 'N/A'), getattr(r, 'substream_name', None)) for r in results]}"
        assert "approved" in result_data


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


class TestCanonicalSecurityValidationProcessor:
    """Test SecurityValidationProcessor canonical implementation."""

    @pytest.fixture
    def security_processor(self):
        """Create SecurityValidationProcessor instance."""
        return SecurityValidationProcessor()

    @pytest.fixture
    def tool_input_data(self):
        """Create ToolInputData instance."""
        return ToolInputData(
            tool_name="Write",
            tool_input={"file_path": "/test/file.py", "content": "print('hello')"},
            context="Test operation",
        )

    def test_match_with_tool_input_data(self, security_processor, tool_input_data):
        """Test match method with ToolInputData part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart.from_dataclass(dataclass=tool_input_data)
        result = security_processor.match(part)

        assert result is True

    def test_match_with_non_tool_input_data(self, security_processor):
        """Test match method with non-ToolInputData part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart("regular text")
        result = security_processor.match(part)

        assert result is False

    @pytest.mark.asyncio
    async def test_call_with_approved_operation(
        self, security_processor, tool_input_data
    ):
        """Test call method with approved operation."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart.from_dataclass(dataclass=tool_input_data)

        results = []
        async for result in security_processor.call(part):
            results.append(result)

        assert len(results) == 1
        security_result = results[0].get_dataclass(SecurityResult)
        assert security_result is not None
        assert security_result.approved is True

    @pytest.mark.asyncio
    async def test_call_with_dangerous_bash_command(self, security_processor):
        """Test call method with dangerous bash command."""
        if not content_api:
            pytest.skip("genai-processors not available")

        dangerous_tool_data = ToolInputData(
            tool_name="Bash",
            tool_input={"command": "rm -rf /"},
            context="Dangerous operation",
        )

        part = content_api.ProcessorPart.from_dataclass(dataclass=dangerous_tool_data)

        results = []
        async for result in security_processor.call(part):
            results.append(result)

        assert len(results) == 1
        security_result = results[0].get_dataclass(SecurityResult)
        assert security_result is not None
        assert security_result.approved is False
        assert "dangerous" in security_result.reason.lower()

    @pytest.mark.asyncio
    async def test_call_with_non_tool_input_data(self, security_processor):
        """Test call method passes through non-ToolInputData parts."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart("regular text")

        results = []
        async for result in security_processor.call(part):
            results.append(result)

        assert len(results) == 1
        assert results[0].text == "regular text"


class TestCanonicalTDDValidationProcessor:
    """Test TDDValidationProcessor canonical implementation."""

    @pytest.fixture
    def tdd_processor(self):
        """Create TDDValidationProcessor instance."""
        return TDDValidationProcessor()

    @pytest.fixture
    def test_file_tool_data(self):
        """Create ToolInputData for test file."""
        return ToolInputData(
            tool_name="Write",
            tool_input={
                "file_path": "/test/test_file.py",
                "content": "def test_something(): pass",
            },
            context="Test file creation",
        )

    def test_match_with_tool_input_data(self, tdd_processor, test_file_tool_data):
        """Test match method with ToolInputData part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart.from_dataclass(dataclass=test_file_tool_data)
        result = tdd_processor.match(part)

        assert result is True

    def test_match_with_non_tool_input_data(self, tdd_processor):
        """Test match method with non-ToolInputData part."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart("regular text")
        result = tdd_processor.match(part)

        assert result is False

    @pytest.mark.asyncio
    async def test_call_with_test_file(self, tdd_processor, test_file_tool_data):
        """Test call method with test file creation."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart.from_dataclass(dataclass=test_file_tool_data)

        results = []
        async for result in tdd_processor.call(part):
            results.append(result)

        assert len(results) == 1
        tdd_result = results[0].get_dataclass(TDDResult)
        assert tdd_result is not None
        assert tdd_result.approved is True
        assert tdd_result.tdd_phase == "red"
        assert tdd_result.test_count == 1

    @pytest.mark.asyncio
    async def test_call_with_non_tdd_relevant_tool(self, tdd_processor):
        """Test call method with non-TDD relevant tool."""
        if not content_api:
            pytest.skip("genai-processors not available")

        bash_tool_data = ToolInputData(
            tool_name="Bash",
            tool_input={"command": "echo hello"},
            context="Bash operation",
        )

        part = content_api.ProcessorPart.from_dataclass(dataclass=bash_tool_data)

        results = []
        async for result in tdd_processor.call(part):
            results.append(result)

        assert len(results) == 1
        tdd_result = results[0].get_dataclass(TDDResult)
        assert tdd_result is not None
        assert tdd_result.approved is True
        assert tdd_result.tdd_phase == "skipped"

    @pytest.mark.asyncio
    async def test_call_with_non_tool_input_data(self, tdd_processor):
        """Test call method passes through non-ToolInputData parts."""
        if not content_api:
            pytest.skip("genai-processors not available")

        part = content_api.ProcessorPart("regular text")

        results = []
        async for result in tdd_processor.call(part):
            results.append(result)

        assert len(results) == 1
        assert results[0].text == "regular text"


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
