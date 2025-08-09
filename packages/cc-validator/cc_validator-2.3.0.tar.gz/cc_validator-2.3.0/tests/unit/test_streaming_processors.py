#!/usr/bin/env python3
"""Test suite for streaming processors to ensure basic functionality."""

import asyncio
import json
import pytest
from typing import AsyncIterable

# Skip tests if genai_processors not available
pytest.importorskip("genai_processors")

from genai_processors import ProcessorPart

from cc_validator.streaming_processors import (
    ValidationProcessor,
    SecurityValidationProcessor,
    TDDValidationProcessor,
    FileCategorizationProcessor,
    ValidationPipelineBuilder,
    ProcessorChain,
    extract_json_from_part,
)


class SimpleTestProcessor(ValidationProcessor):
    """Simple test processor that echoes input with a prefix"""

    def __init__(self, prefix: str = "TEST"):
        super().__init__()
        self.prefix = prefix

    def match(self, part: ProcessorPart) -> bool:
        """Match JSON parts with test field"""
        json_data = extract_json_from_part(part)
        return "test" in json_data

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the test part"""
        json_data = extract_json_from_part(part)
        if json_data and "test" in json_data:
            test_data = json_data.copy()
            test_data["processed"] = f"{self.prefix}: {test_data.get('test', '')}"
            yield ProcessorPart(json.dumps(test_data))
        else:
            yield part


class TestStreamingProcessors:
    """Test basic streaming processor functionality"""

    def test_processor_instantiation(self) -> None:
        """Test that processors can be instantiated"""
        assert ValidationProcessor()
        assert SecurityValidationProcessor()
        assert TDDValidationProcessor()
        assert FileCategorizationProcessor()

    def test_pipeline_builder(self) -> None:
        """Test pipeline builder creates processors"""
        builder = ValidationPipelineBuilder()

        assert builder.create_security_pipeline()
        assert builder.create_tdd_pipeline()
        assert builder.create_file_categorization_pipeline()
        assert builder.create_parallel_pipeline()

        # Test chained pipeline
        processors = [SimpleTestProcessor("PROC1"), SimpleTestProcessor("PROC2")]
        chain = builder.create_chained_pipeline(processors)
        assert isinstance(chain, ProcessorChain)

    @pytest.mark.asyncio
    async def test_simple_processor_flow(self) -> None:
        """Test simple processor with async streaming"""
        processor = SimpleTestProcessor("PROCESSED")

        input_data = {"test": "hello world"}
        input_part = ProcessorPart(json.dumps(input_data))

        results = []
        async for output_part in processor.call(input_part):
            json_data = extract_json_from_part(output_part)
            if json_data:
                results.append(json_data)

        assert len(results) == 1
        assert results[0]["test"] == "hello world"
        assert results[0]["processed"] == "PROCESSED: hello world"

    @pytest.mark.asyncio
    async def test_processor_chaining(self) -> None:
        """Test chaining multiple processors using the + operator"""
        proc1 = SimpleTestProcessor("FIRST")
        proc2 = SimpleTestProcessor("SECOND")

        # Chain processors using the + operator
        chained = proc1 + proc2

        input_data = {"test": "data"}
        input_part = ProcessorPart(json.dumps(input_data))

        results = []
        async for output_part in chained.call(input_part):
            json_data = extract_json_from_part(output_part)
            if json_data:
                results.append(json_data)

        # The chained processor should process the data through both processors
        # We expect to see the final result with both processors applied
        assert len(results) > 0
        # The final result should have been processed by SECOND processor
        # since it processes the output of FIRST
        assert any(r.get("processed", "").startswith("SECOND:") for r in results)

    @pytest.mark.asyncio
    async def test_custom_processor_chain(self) -> None:
        """Test custom ProcessorChain implementation"""
        proc1 = SimpleTestProcessor("FIRST")
        proc2 = SimpleTestProcessor("SECOND")

        # Create chain using ProcessorChain
        chain = ProcessorChain([proc1, proc2])

        input_data = {"test": "data"}
        from genai_processors import streams

        input_stream = streams.stream_content([ProcessorPart(json.dumps(input_data))])

        results = []
        async for part in chain(input_stream):
            json_data = extract_json_from_part(part)
            if json_data:
                results.append(json_data)

        # Should have both results
        assert any(r.get("processed", "").startswith("FIRST:") for r in results)
        assert any(r.get("processed", "").startswith("SECOND:") for r in results)

    @pytest.mark.asyncio
    async def test_validation_processor_base(self) -> None:
        """Test base validation processor functionality"""
        processor = ValidationProcessor()

        # Should have default match method
        text_part = ProcessorPart("test")
        assert processor.match(text_part)

        # Should yield the same part by default
        result_parts = []
        async for part in processor.call(text_part):
            result_parts.append(part)

        assert len(result_parts) == 1
        assert result_parts[0] == text_part

    @pytest.mark.asyncio
    async def test_multiple_processor_chaining(self) -> None:
        """Test chaining multiple processors using multiple + operators"""
        proc1 = SimpleTestProcessor("FIRST")
        proc2 = SimpleTestProcessor("SECOND")
        proc3 = SimpleTestProcessor("THIRD")

        # Chain multiple processors using + operators
        chained = proc1 + proc2 + proc3

        input_data = {"test": "data"}
        input_part = ProcessorPart(json.dumps(input_data))

        results = []
        async for output_part in chained.call(input_part):
            json_data = extract_json_from_part(output_part)
            if json_data:
                results.append(json_data)

        # Should have processed through all three processors
        assert len(results) > 0
        # The final result should have been processed by THIRD processor
        # since it processes the output of SECOND which processes the output of FIRST
        assert any(r.get("processed", "").startswith("THIRD:") for r in results)

    @pytest.mark.asyncio
    async def test_parallel_validation_pattern(self) -> None:
        """Test parallel validation pattern with mock processors"""

        async def mock_security_process() -> dict[str, object]:
            await asyncio.sleep(0.01)  # Simulate processing
            return {"approved": True, "reason": "Security check passed"}

        async def mock_tdd_process() -> dict[str, object]:
            await asyncio.sleep(0.01)  # Simulate processing
            return {
                "approved": True,
                "reason": "TDD check passed",
                "tdd_phase": "green",
            }

        # Run in parallel
        results = await asyncio.gather(mock_security_process(), mock_tdd_process())

        assert len(results) == 2
        assert results[0]["approved"] is True
        assert results[1]["approved"] is True
        assert results[1]["tdd_phase"] == "green"


def run_tests() -> None:
    """Run the streaming processor tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()
