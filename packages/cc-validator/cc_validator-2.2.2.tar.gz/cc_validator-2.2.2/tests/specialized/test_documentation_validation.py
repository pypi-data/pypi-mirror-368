#!/usr/bin/env python3

import asyncio
import os
import sys
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_validator.security_validator import SecurityValidator
from cc_validator.file_categorization import FileContextAnalyzer


def test_documentation_file_skips_analysis() -> None:
    """Test that documentation files skip code security analysis"""
    validator = SecurityValidator()

    # Test various documentation files
    doc_files = [
        ("docs/WEB-TESTING-STRATEGY.md", "# Web Testing Strategy\n\n" + "x" * 600),
        ("README.md", "# Project README\n\n" + "y" * 700),
        ("docs/ARCHITECTURE.md", "# Architecture\n\n" + "z" * 800),
        ("CONTRIBUTING.md", "# Contributing Guidelines\n\n" + "a" * 900),
    ]

    for file_path, content in doc_files:
        tool_input = {"file_path": file_path, "content": content}

        # Mock the upload_file_for_analysis to track if it was called
        with patch.object(validator, "upload_file_for_analysis") as mock_upload:
            result = asyncio.run(validator.validate("Write", tool_input, ""))

            # Documentation files should NOT trigger file upload/analysis
            mock_upload.assert_not_called()

            # Should be approved without file analysis
            assert result[
                "approved"
            ], f"Documentation file {file_path} should be approved"
            print(f"✓ {file_path} correctly skipped file analysis")


def test_code_files_trigger_analysis() -> None:
    """Test that code files still trigger analysis when >500 chars"""
    validator = SecurityValidator(api_key="test_key")

    # Test code files that should trigger analysis
    code_files = [
        ("src/main.py", "import os\n\n" + "def func():\n    pass\n" * 150),
        (
            "lib/handler.js",
            "const express = require('express');\n\n" + "function handler() {}\n" * 100,
        ),
    ]

    for file_path, content in code_files:
        tool_input = {"file_path": file_path, "content": content}

        # Mock the upload_file_for_analysis to track if it was called
        with patch.object(
            validator, "upload_file_for_analysis", return_value=None
        ) as mock_upload:
            with patch.object(validator, "client", Mock()):
                asyncio.run(validator.validate("Write", tool_input, ""))

                # Code files >500 chars should trigger file upload
                mock_upload.assert_called_once()
                print(f"✓ {file_path} correctly triggered file analysis")


def test_file_categorization_order() -> None:
    """Test that file categorization happens before file analysis"""
    validator = SecurityValidator(api_key="test_key")

    # Create a large documentation file
    doc_content = "# Documentation\n\n" + "This is documentation content.\n" * 100
    tool_input = {"file_path": "docs/GUIDE.md", "content": doc_content}

    # Track method call order
    call_order = []

    # Mock FileContextAnalyzer.categorize_file
    original_categorize = FileContextAnalyzer.categorize_file

    def mock_categorize(file_path: str, content: str) -> dict[str, Any]:
        call_order.append("categorize_file")
        return original_categorize(file_path, content)

    # Mock upload_file_for_analysis
    def mock_upload(file_path: str, content: str) -> None:
        call_order.append("upload_file_for_analysis")
        return None

    with patch.object(
        FileContextAnalyzer, "categorize_file", side_effect=mock_categorize
    ):
        with patch.object(
            validator, "upload_file_for_analysis", side_effect=mock_upload
        ):
            result = asyncio.run(validator.validate("Write", tool_input, ""))

    # Verify categorization happened first
    assert "categorize_file" in call_order, "categorize_file should be called"
    assert (
        "upload_file_for_analysis" not in call_order
    ), "upload_file_for_analysis should NOT be called for docs"
    assert result["approved"]
    print("✓ File categorization correctly happens before upload decision")


def test_test_files_skip_strict_analysis() -> None:
    """Test that test files skip strict security analysis"""
    validator = SecurityValidator()

    test_files = [
        (
            "tests/test_feature.py",
            "def test_something():\n    api_key = 'test_key_12345678901234567890'\n"
            * 50,
        ),
        (
            "spec/feature.spec.js",
            "describe('feature', () => {\n    const token = 'mock_token_abcdefghijklmnop';\n"
            * 50,
        ),
    ]

    for file_path, content in test_files:
        tool_input = {"file_path": file_path, "content": content}

        with patch.object(validator, "upload_file_for_analysis") as mock_upload:
            result = asyncio.run(validator.validate("Write", tool_input, ""))

            # Test files should not trigger upload
            mock_upload.assert_not_called()

            # Should be approved (test fixtures allowed)
            assert result[
                "approved"
            ], f"Test file {file_path} should allow test fixtures"
            print(f"✓ {file_path} correctly allows test fixtures")


def test_config_files_skip_analysis() -> None:
    """Test that config files skip code analysis"""
    validator = SecurityValidator()

    config_files = [
        ("pyproject.toml", "[tool.pytest]\n" * 100),
        ("package.json", '{"name": "test", "dependencies": {}}\n' * 50),
        (".env.example", "API_KEY=your_key_here\n" * 100),
    ]

    for file_path, content in config_files:
        tool_input = {"file_path": file_path, "content": content}

        with patch.object(validator, "upload_file_for_analysis") as mock_upload:
            result = asyncio.run(validator.validate("Write", tool_input, ""))

            # Config files should not trigger upload
            mock_upload.assert_not_called()
            assert result["approved"]
            print(f"✓ {file_path} correctly skipped as config file")


if __name__ == "__main__":
    print("Testing documentation validation scenarios...\n")

    test_documentation_file_skips_analysis()
    print()

    test_code_files_trigger_analysis()
    print()

    test_file_categorization_order()
    print()

    test_test_files_skip_strict_analysis()
    print()

    test_config_files_skip_analysis()
    print()

    print("\n✅ All documentation validation tests passed!")
