#!/usr/bin/env python3
"""Basic test to verify processor setup is working"""

import pytest


def test_processor_imports() -> None:
    """Test that we can import our processors"""
    from cc_validator.streaming_processors import (
        ValidationProcessor,  # noqa: F401
        SecurityValidationProcessor,  # noqa: F401
        TDDValidationProcessor,  # noqa: F401
        FileCategorizationProcessor,  # noqa: F401
        ValidationPipelineBuilder,  # noqa: F401
    )


def test_processor_creation() -> None:
    """Test that processors can be instantiated"""
    from cc_validator.streaming_processors import (
        ValidationProcessor,
        SecurityValidationProcessor,
        TDDValidationProcessor,
        FileCategorizationProcessor,
        ValidationPipelineBuilder,
    )

    val_proc = ValidationProcessor()
    sec_proc = SecurityValidationProcessor()
    tdd_proc = TDDValidationProcessor()
    file_proc = FileCategorizationProcessor()
    builder = ValidationPipelineBuilder()

    assert val_proc is not None
    assert sec_proc is not None
    assert tdd_proc is not None
    assert file_proc is not None
    assert builder is not None


def test_processor_attributes() -> None:
    """Test that processors have expected attributes"""
    from cc_validator.streaming_processors import (
        SecurityValidationProcessor,
        TDDValidationProcessor,
    )

    sec_proc = SecurityValidationProcessor()
    tdd_proc = TDDValidationProcessor()

    assert hasattr(sec_proc, "processor_type")
    assert sec_proc.processor_type == "security"

    assert hasattr(tdd_proc, "processor_type")
    assert tdd_proc.processor_type == "tdd"


@pytest.mark.asyncio
async def test_basic_validation_flow() -> None:
    """Test basic validation flow without genai-processors specifics"""
    from cc_validator.security_validator import SecurityValidator

    sec_validator = SecurityValidator()

    result = await sec_validator.perform_quick_validation("Bash", {"command": "ls -la"})
    assert result["approved"] is True  # Safe commands are allowed

    result = await sec_validator.perform_quick_validation(
        "Bash", {"command": "rm -rf /"}
    )
    assert result["approved"] is False

    result = await sec_validator.perform_quick_validation(
        "Bash", {"command": "grep pattern file.txt"}
    )
    assert result["approved"] is False

    result = await sec_validator.perform_quick_validation(
        "Bash", {"command": "echo 'test' && eval \"echo $USER\""}
    )
    assert result["approved"] is False

    result = await sec_validator.perform_quick_validation(
        "Bash", {"command": "echo 'ZWNobyBoZWxsbw==' | base64 -d | sh"}
    )
    assert result["approved"] is False

    result = await sec_validator.perform_quick_validation(
        "Write",
        {
            "file_path": "app.py",
            "content": "import subprocess\nsubprocess.run(cmd, shell=True)",
        },
    )
    assert result["approved"] is False
