#!/usr/bin/env python3
"""
Test that Edit/MultiEdit operations properly read file content for TDD validation.
This tests the fix for the bug where Edit/MultiEdit were bypassing TDD by not reading file content.
"""

import os
import tempfile
import pytest
import asyncio
from cc_validator.canonical_pipeline import CanonicalPipelineValidator
from cc_validator.file_storage import FileStorage
from cc_validator.config import ProcessorConfig


@pytest.mark.asyncio
@pytest.mark.comprehensive
async def test_edit_reads_file_content_for_tdd():
    """Test that Edit operations read file content and enforce TDD"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    # Clear test data to prevent interference
    from cc_validator.file_storage import FileStorage

    storage = FileStorage()
    storage.cleanup_expired_data()

    # Also clear the specific test results
    if os.path.exists(storage.test_results_file):
        os.remove(storage.test_results_file)

    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create main.py with implementation
        main_py = os.path.join(temp_dir, "main.py")
        implementation_content = """def calculate(x, y):
    return x + y

def main():
    result = calculate(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
        with open(main_py, "w") as f:
            f.write(implementation_content)

        # Try to edit without tests - should be blocked
        result = await validator.validate_tool_use_async(
            "Edit",
            {
                "file_path": main_py,
                "old_string": "return x + y",
                "new_string": "return x + y + 1",
            },
            "Fixing calculation",
        )

        # Should be blocked by TDD
        assert not result["approved"], "Edit should be blocked without tests"
        assert "TDD" in result["reason"], "Should be blocked by TDD validation"
        assert result.get("tdd_approved") is False


@pytest.mark.asyncio
@pytest.mark.comprehensive
async def test_multiedit_reads_file_content_for_tdd():
    """Test that MultiEdit operations read file content and enforce TDD"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    # Clear test data to prevent interference
    from cc_validator.file_storage import FileStorage

    storage = FileStorage()
    storage.cleanup_expired_data()

    # Also clear the specific test results
    if os.path.exists(storage.test_results_file):
        os.remove(storage.test_results_file)

    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create app.py with implementation
        app_py = os.path.join(temp_dir, "app.py")
        implementation_content = """class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

def process_data(data):
    calc = Calculator()
    total = 0
    for item in data:
        total = calc.add(total, item)
    return total
"""
        with open(app_py, "w") as f:
            f.write(implementation_content)

        # Try MultiEdit without tests - should be blocked
        result = await validator.validate_tool_use_async(
            "MultiEdit",
            {
                "file_path": app_py,
                "edits": [
                    {"old_string": "return a + b", "new_string": "return a + b + 0.0"},
                    {"old_string": "return a * b", "new_string": "return a * b * 1.0"},
                ],
            },
            "Converting to float operations",
        )

        # Should be blocked by TDD
        assert not result["approved"], "MultiEdit should be blocked without tests"
        assert "TDD" in result["reason"], "Should be blocked by TDD validation"
        assert result.get("tdd_approved") is False


@pytest.mark.asyncio
@pytest.mark.comprehensive
async def test_edit_on_different_file_types():
    """Test Edit operations categorize different file types correctly"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    # Ensure we're on a feature branch for testing
    os.environ["CLAUDE_TEST_BRANCH"] = "feature-test-branch"

    # Clear test data to prevent interference
    from cc_validator.file_storage import FileStorage

    storage = FileStorage()
    storage.cleanup_expired_data()

    # Also clear the specific test results
    if os.path.exists(storage.test_results_file):
        os.remove(storage.test_results_file)

    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Test 1: main.py (should require TDD)
        main_py = os.path.join(temp_dir, "main.py")
        with open(main_py, "w") as f:
            f.write("def main():\n    print('hello')\n")

        result = await validator.validate_tool_use_async(
            "Edit",
            {
                "file_path": main_py,
                "old_string": "print('hello')",
                "new_string": "print('world')",
            },
            "",
        )
        assert not result["approved"], "main.py edit should be blocked by TDD"

        # Test 2: README.md (should not require TDD)
        readme = os.path.join(temp_dir, "README.md")
        with open(readme, "w") as f:
            f.write("# Project\n\nDescription here.")

        result = await validator.validate_tool_use_async(
            "Edit",
            {
                "file_path": readme,
                "old_string": "Description here.",
                "new_string": "Updated description.",
            },
            "",
        )
        assert result["approved"], "README.md edit should be allowed"

        # Test 3: __init__.py with no implementation (should not require TDD)
        init_py = os.path.join(temp_dir, "__init__.py")
        with open(init_py, "w") as f:
            f.write("__version__ = '1.0.0'\n")

        result = await validator.validate_tool_use_async(
            "Edit",
            {
                "file_path": init_py,
                "old_string": "__version__ = '1.0.0'",
                "new_string": "__version__ = '1.0.1'",
            },
            "",
        )
        assert result[
            "approved"
        ], "__init__.py without implementation should be allowed"


@pytest.mark.asyncio
@pytest.mark.quick
async def test_edit_nonexistent_file():
    """Test Edit on non-existent file is handled properly"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    # Edit non-existent file
    result = await validator.validate_tool_use_async(
        "Edit",
        {
            "file_path": "/tmp/nonexistent_file_12345.py",
            "old_string": "old",
            "new_string": "new",
        },
        "",
    )

    # Should still validate (might be blocked for other reasons)
    assert "approved" in result
    assert "reason" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
