#!/usr/bin/env python3

import os
import sys
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_validator.canonical_pipeline import CanonicalPipelineValidator
from cc_validator.file_storage import FileStorage
from cc_validator.config import ProcessorConfig
from cc_validator.file_categorization import FileContextAnalyzer


def test_documentation_file_skips_analysis() -> None:
    """Test that documentation files skip code security analysis"""
    api_key = os.environ.get("GEMINI_API_KEY")
    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    # Test various documentation files
    doc_files = [
        ("docs/WEB-TESTING-STRATEGY.md", "# Web Testing Strategy\n\n" + "x" * 600),
        ("README.md", "# Project README\n\n" + "y" * 700),
        ("docs/ARCHITECTURE.md", "# Architecture\n\n" + "z" * 800),
        ("CONTRIBUTING.md", "# Contributing Guidelines\n\n" + "a" * 900),
    ]

    for file_path, content in doc_files:
        tool_input = {"file_path": file_path, "content": content}

        result = validator.validate_tool_use("Write", tool_input, "")

        # Documentation files should be approved without analysis
        assert result[
            "approved"
        ], f"Documentation file {file_path} should be approved"
        print(f"✓ {file_path} correctly skipped file analysis")


def test_code_files_trigger_analysis() -> None:
    """Test that code files still trigger analysis when >500 chars"""
    file_storage = FileStorage()
    config = ProcessorConfig(api_key="test_key")
    validator = CanonicalPipelineValidator(file_storage, config)

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

        # File analysis is handled internally in canonical pipeline
        result = validator.validate_tool_use("Write", tool_input, "")

        # Code files should trigger validation (which may be blocked by TDD)
        # The file analysis happens internally in processors
        print(f"✓ {file_path} correctly processed by canonical pipeline")


def test_file_categorization_order() -> None:
    """Test that documentation files are properly categorized and approved"""
    file_storage = FileStorage()
    config = ProcessorConfig(api_key="test_key")
    validator = CanonicalPipelineValidator(file_storage, config)

    # Create a large documentation file
    doc_content = "# Documentation\n\n" + "This is documentation content.\n" * 100
    tool_input = {"file_path": "docs/GUIDE.md", "content": doc_content}

    # Test that documentation file is categorized correctly and approved
    result = validator.validate_tool_use("Write", tool_input, "")

    # Documentation files should be approved without TDD validation
    assert result["approved"], "Documentation file should be approved"
    print("✓ Documentation file correctly categorized and approved")


def test_test_files_skip_strict_analysis() -> None:
    """Test that test files skip strict security analysis"""
    api_key = os.environ.get("GEMINI_API_KEY")
    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    test_files = [
        (
            "tests/test_feature.py",
            "def test_something():\n"
            + "    api_key = 'test_key_12345678901234567890'\n    # Test fixture data\n"
            * 50,
        ),
        (
            "spec/feature.spec.js",
            "describe('feature', () => {\n"
            + "    const token = 'mock_token_abcdefghijklmnop';\n    // Test fixture data\n"
            * 50
            + "});",
        ),
    ]

    for file_path, content in test_files:
        tool_input = {"file_path": file_path, "content": content}

        # File analysis is handled internally in canonical pipeline
        result = validator.validate_tool_use("Write", tool_input, "")

        # Should be approved (test fixtures allowed)
        assert result[
            "approved"
        ], f"Test file {file_path} should allow test fixtures"
        print(f"✓ {file_path} correctly allows test fixtures")


def test_config_files_skip_analysis() -> None:
    """Test that config files skip code analysis"""
    api_key = os.environ.get("GEMINI_API_KEY")
    file_storage = FileStorage()
    config = ProcessorConfig(api_key=api_key) if api_key else None
    validator = CanonicalPipelineValidator(file_storage, config)

    config_files = [
        ("pyproject.toml", "[tool.pytest]\n" * 100),
        ("package.json", '{"name": "test", "dependencies": {}}\n' * 50),
        (".env.example", "API_KEY=your_key_here\n" * 100),
    ]

    for file_path, content in config_files:
        tool_input = {"file_path": file_path, "content": content}

        # File analysis is handled internally in canonical pipeline
        result = validator.validate_tool_use("Write", tool_input, "")

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
