#!/usr/bin/env python3
"""
File categorization tests using pytest markers.
"""

import os
import pytest
from cc_validator.file_categorization import FileContextAnalyzer

# Static categorization tests


@pytest.mark.static
@pytest.mark.quick
@pytest.mark.parametrize(
    "file_path, content, expected_category, expected_is_test, expected_strict",
    [
        ("test_calculator.py", "", "test", True, False),
        ("tests/test_utils.py", "", "test", True, False),
        ("test/test_main.py", "", "test", True, False),
        ("spec_calculator.py", "", "test", True, False),
        ("tests/conftest.py", "import pytest", "test", True, False),
        ("auth.py", "def test_login():\n    assert True", "test", True, False),
        (
            "utils.py",
            "import pytest\n\ndef test_helper():\n    pass",
            "test",
            True,
            False,
        ),
        (
            "check.py",
            "class TestAuth:\n    def test_user(self):\n        pass",
            "test",
            True,
            False,
        ),
    ],
)
def test_static_test_files(
    file_path, content, expected_category, expected_is_test, expected_strict
):
    """Test that test files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category
    assert result["is_test_file"] == expected_is_test
    assert result["requires_strict_security"] == expected_strict


@pytest.mark.static
@pytest.mark.quick
@pytest.mark.parametrize(
    "file_path, content, expected_category, expected_is_test, expected_strict",
    [
        ("README.md", "# Project Title", "docs", False, False),
        ("CHANGELOG.md", "## Version 1.0.0", "docs", False, False),
        ("docs/api.rst", "API Documentation", "docs", False, False),
        ("guide.txt", "User guide content", "docs", False, False),
        (
            "docs/GCP-SETUP-PLAN.md",
            "# GCP Setup Plan\n\n## Steps",
            "docs",
            False,
            False,
        ),
        ("LICENSE.txt", "MIT License", "docs", False, False),
        ("CONTRIBUTING.md", "# How to Contribute", "docs", False, False),
    ],
)
def test_static_documentation_files(
    file_path, content, expected_category, expected_is_test, expected_strict
):
    """Test that documentation files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category
    assert result["is_test_file"] == expected_is_test
    assert result["requires_strict_security"] == expected_strict


@pytest.mark.static
@pytest.mark.quick
@pytest.mark.parametrize(
    "file_path, content, expected_category",
    [
        ("setup.py", "from setuptools import setup", "config"),
        ("pyproject.toml", "[tool.pytest]", "config"),
        ("requirements.txt", "pytest==7.0.0", "docs"),
        ("Dockerfile", "FROM python:3.11", "config"),
        ("config.json", '{"debug": true}', "config"),
        (".env.example", "DATABASE_URL=postgres://localhost", "config"),
    ],
)
def test_static_configuration_files(file_path, content, expected_category):
    """Test that configuration files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category


@pytest.mark.static
@pytest.mark.parametrize(
    "file_path, content, expected_category",
    [
        ("__init__.py", "", "structural"),
        ("__init__.py", "from .module import function", "structural"),
        ("__main__.py", "import sys", "structural"),
        ("constants.py", "__version__ = '1.0'", "structural"),
    ],
)
def test_static_structural_files(file_path, content, expected_category):
    """Test that structural files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category


@pytest.mark.static
@pytest.mark.parametrize(
    "file_path, content, expected_category, expected_strict",
    [
        ("calculator.py", "def add(a, b):\n    return a + b", "implementation", True),
        (
            "app.py",
            "def process_payment(amount):\n    return charge_card(amount)",
            "implementation",
            True,
        ),
        (
            "server.py",
            "from flask import Flask\napp = Flask(__name__)",
            "implementation",
            True,
        ),
        (
            "__init__.py",
            "def factory():\n    return SomeClass()",
            "implementation",
            True,
        ),
    ],
)
def test_static_implementation_files(
    file_path, content, expected_category, expected_strict
):
    """Test that implementation files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category
    assert result["requires_strict_security"] == expected_strict


@pytest.mark.static
@pytest.mark.parametrize(
    "file_path, content, expected_category",
    [
        ("package-lock.json", '{"name": "project", "lockfileVersion": 1}', "config"),
        ("schema.sql", "CREATE TABLE users (id INT PRIMARY KEY);", "data"),
    ],
)
def test_static_data_files(file_path, content, expected_category):
    """Test that data files are correctly identified by static analysis."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category


@pytest.mark.static
def test_edge_cases():
    """Test edge cases in static categorization."""
    result = FileContextAnalyzer.categorize_file("calculator.py", "")
    assert result["category"] == "implementation"

    result = FileContextAnalyzer.categorize_file(
        "settings.py", "if DEBUG:\n    DATABASE_URL = 'sqlite:///test.db'"
    )
    assert result["category"] == "implementation"


@pytest.mark.static
@pytest.mark.quick
def test_test_secret_patterns():
    """Test that test secret patterns are available."""
    patterns = FileContextAnalyzer.get_test_secret_patterns()
    expected_patterns = ["test[_-]", "mock[_-]", "dummy[_-]", "fake[_-]", "example[_-]"]
    for expected in expected_patterns:
        assert expected in patterns


# Additional static categorization tests for implementation files


@pytest.mark.static
@pytest.mark.quick
@pytest.mark.parametrize(
    "file_path, content, expected_category, expected_requires_strict",
    [
        ("calculator.py", "def add(a, b):\n    return a + b", "implementation", True),
        (
            "utils.py",
            "def helper():\n    return do_something()",
            "implementation",
            True,
        ),
        (
            "service.py",
            "class UserService:\n    def create_user(self):\n        pass",
            "implementation",
            True,
        ),
    ],
)
def test_static_implementation_files_require_strict_security(
    file_path, content, expected_category, expected_requires_strict
):
    """Test that implementation files require strict security with static categorization."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category
    assert result["requires_strict_security"] == expected_requires_strict


@pytest.mark.static
@pytest.mark.quick
@pytest.mark.parametrize(
    "file_path, content, expected_category, expected_requires_strict",
    [
        ("test_calculator.py", "def test_add():\n    assert True", "test", False),
        (
            "tests/test_utils.py",
            "import pytest\n\ndef test_helper():\n    pass",
            "test",
            False,
        ),
    ],
)
def test_static_test_files_skip_strict_security(
    file_path, content, expected_category, expected_requires_strict
):
    """Test that test files do not require strict security with static categorization."""
    result = FileContextAnalyzer.categorize_file(file_path, content)
    assert result["category"] == expected_category
    assert result["requires_strict_security"] == expected_requires_strict


# Consistency tests


@pytest.mark.comprehensive
@pytest.mark.parametrize(
    "file_path, content, expected_category",
    [
        ("test_example.py", "def test_something(): pass", "test"),
        ("README.md", "# Documentation", "docs"),
        ("setup.py", "from setuptools import setup", "config"),
        ("__init__.py", "", "structural"),
    ],
)
def test_static_vs_api_consistency(file_path, content, expected_category):
    """Verify static categorization aligns with API expectations."""
    static_result = FileContextAnalyzer.categorize_file(file_path, content)
    assert static_result["category"] == expected_category
    if expected_category == "test":
        assert static_result["is_test_file"] is True
        assert static_result["requires_strict_security"] is False
