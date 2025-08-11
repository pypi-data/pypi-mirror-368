#!/usr/bin/env python3
"""
Comprehensive file categorization tests including hybrid categorization system.

This test suite combines:
1. Static file categorization tests with pytest markers
2. Hybrid categorization tests with fast path and LLM fallback verification
"""

import os
import time
import pytest
from unittest.mock import Mock, AsyncMock, patch
from cc_validator.file_categorization import FileContextAnalyzer

# TDDValidationPipeline removed - using validation_logic instead
from cc_validator.file_storage import FileStorage

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


# Hybrid categorization tests from test_hybrid_categorization.py


class TestHybridCategorization:
    """Test the hybrid categorization approach with fast path and LLM fallback"""

    @pytest.fixture
    def file_analyzer(self) -> FileContextAnalyzer:
        """Create a file context analyzer instance"""
        return FileContextAnalyzer()

    # TDDValidationPipeline fixture removed - no longer needed after dead code cleanup

    def test_fast_path_test_files(self, file_analyzer: FileContextAnalyzer) -> None:
        """Test that test files are correctly identified by fast path"""
        test_cases = [
            ("test_something.py", "test"),
            ("something_test.py", "test"),
            ("module_test.go", "test"),  # Go convention: *_test.go
            ("user_test.go", "test"),
            ("test.py", None),  # Ambiguous - could be test or not
            ("something.spec.ts", "test"),
            ("component.test.js", "test"),
            ("__tests__/component.js", "test"),
            ("tests/integration_test.py", "test"),
            ("src/test/java/TestClass.java", "test"),
        ]

        for file_path, expected_category in test_cases:
            result = file_analyzer.categorize_file(file_path)
            if expected_category is None:
                # File needs deeper analysis, but static categorization makes a best guess
                assert result["category"] in [
                    "test",
                    "implementation",
                ], f"Failed for {file_path}"
            else:
                assert (
                    result["category"] == expected_category
                ), f"Failed for {file_path}"

    def test_fast_path_documentation_files(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that documentation files are correctly identified by fast path"""
        test_cases = [
            ("README.md", "docs"),
            ("CHANGELOG.md", "docs"),
            ("LICENSE", None),  # No extension, needs LLM
            ("LICENSE.md", "docs"),  # With extension, fast path works
            ("CONTRIBUTING.md", "docs"),
            ("docs/api.md", "docs"),
            ("documentation/guide.rst", "docs"),
            ("wiki/page.md", "docs"),
            ("ROADMAP.txt", "docs"),
            ("AUTHORS", None),  # No extension, needs LLM
            ("doc/tutorial.adoc", "docs"),
        ]

        for file_path, expected_category in test_cases:
            result = file_analyzer.categorize_file(file_path)
            if expected_category is None:
                # File needs deeper analysis, but static categorization makes a best guess
                assert result["category"] in [
                    "test",
                    "implementation",
                ], f"Failed for {file_path}"
            else:
                assert (
                    result["category"] == expected_category
                ), f"Failed for {file_path}"

    def test_fast_path_config_files(self, file_analyzer: FileContextAnalyzer) -> None:
        """Test that configuration files are correctly identified by fast path"""
        test_cases = [
            (".gitignore", "config"),
            ("package.json", "config"),
            ("pyproject.toml", "config"),
            ("Cargo.toml", "config"),
            ("tsconfig.json", "config"),
            ("jest.config.js", "config"),  # This is in the known list
            (".eslintrc.js", None),  # Not in known list, needs LLM
            ("Dockerfile", "config"),
            ("docker-compose.yml", "config"),
            ("requirements.txt", "docs"),  # .txt extension matches docs first
            ("Gemfile", None),  # Not in known list, needs LLM
            (".env", None),  # Not in known list, needs LLM
            ("config.yml", "config"),  # Has .yml extension
            ("settings.json", "config"),  # Has .json extension
        ]

        for file_path, expected_category in test_cases:
            result = file_analyzer.categorize_file(file_path)
            if expected_category is None:
                # File needs deeper analysis, but static categorization makes a best guess
                assert result["category"] in [
                    "test",
                    "implementation",
                ], f"Failed for {file_path}"
            else:
                assert (
                    result["category"] == expected_category
                ), f"Failed for {file_path}"

    def test_fast_path_structural_files(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that potential structural files need LLM verification"""
        # These files could be structural or implementation - fast path returns None
        ambiguous_structural_files = [
            "__init__.py",  # Could have imports or be empty
            "index.js",  # Could be barrel file or have logic
            "index.ts",  # Could be barrel file or have logic
            "mod.rs",  # Could be module declaration or have logic
            "constants.py",  # Not in structural list - could have logic
            "types.ts",  # Not in structural list - could have validation
            "doc.go",  # Could be docs or have logic
            "main.go",  # Could be minimal or have logic
        ]

        for file_path in ambiguous_structural_files:
            result = file_analyzer.categorize_file(file_path)
            # Without content, these files get categorized as structural or implementation
            assert result["category"] in [
                "structural",
                "implementation",
            ], f"Unexpected category for {file_path}: {result['category']}"

    def test_fast_path_generated_files(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that generated files are correctly identified by fast path"""
        test_cases = [
            ("schema.generated.ts", None),  # Generated files need LLM
            ("types.g.dart", None),  # Generated files need LLM
            ("model.freezed.dart", None),  # Generated files need LLM
            ("proto_pb.go", None),  # Doesn't match pattern - needs dot before pb
            ("proto.pb.go", None),  # Generated files need LLM
            ("api.pb.py", None),  # Generated files need LLM
            ("api_pb2.py", None),  # Generated files need LLM
            ("autogen_schema.py", None),  # Doesn't match - no pattern for autogen_
            ("api_generated.py", None),  # Generated files need LLM
            ("package-lock.json", "config"),  # .json extension matches config
            ("yarn.lock", None),  # No matching pattern
            ("Cargo.lock", None),  # No matching pattern
            ("go.sum", None),  # Lock files need LLM
        ]

        for file_path, expected_category in test_cases:
            result = file_analyzer.categorize_file(file_path)
            if expected_category is None:
                # File needs deeper analysis, but static categorization makes a best guess
                assert result["category"] in [
                    "test",
                    "implementation",
                ], f"Failed for {file_path}"
            else:
                assert (
                    result["category"] == expected_category
                ), f"Failed for {file_path}"

    def test_fast_path_data_files(self, file_analyzer: FileContextAnalyzer) -> None:
        """Test that data files are correctly identified by fast path"""
        test_cases = [
            ("data.json", "config"),  # .json is config, not data
            ("dataset.csv", None),  # Data files need LLM
            ("fixtures/users.json", "config"),  # .json is config
            ("testdata/sample.xml", None),  # Data files need LLM
            ("mock_data.json", "config"),  # .json is config
            ("seeds/test.sql", None),  # Data files need LLM
            ("config.yaml", "config"),  # .yaml is config
            ("data/values.xml", None),  # Data files need LLM
            ("log.jsonl", None),  # Data files need LLM
            ("stream.ndjson", None),  # Data files need LLM
        ]

        for file_path, expected_category in test_cases:
            result = file_analyzer.categorize_file(file_path)
            if expected_category is None:
                # Data files without recognized extensions get categorized as implementation
                assert result["category"] in [
                    "data",
                    "implementation",
                ], f"Failed for {file_path}"
            else:
                assert (
                    result["category"] == expected_category
                ), f"Failed for {file_path}"

    def test_fast_path_returns_ambiguous_as_implementation(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that ambiguous files get categorized as implementation by default"""
        ambiguous_files = [
            "main.py",  # Could be structural or implementation
            "app.js",  # Could be structural or implementation
            "service.go",  # Likely implementation but needs content check
            "utils.py",  # Could be either
            "helper.rs",  # Could be either
            "model.dart",  # Could be either
            "handler.ts",  # Could be either
        ]

        for file_path in ambiguous_files:
            result = file_analyzer.categorize_file(file_path)
            # Without content, these typically get categorized as implementation
            assert (
                result["category"] == "implementation"
            ), f"Expected implementation for ambiguous file {file_path}"

    def test_static_categorization_test_files(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that test files are correctly categorized by static analysis"""
        # Test file should be categorized as test
        result = file_analyzer.categorize_file(
            "test_user.py", "def test_create(): pass"
        )
        assert result["category"] == "test"
        assert "test file" in result["reason"].lower()

        # Documentation should be categorized as docs
        result = file_analyzer.categorize_file("README.md", "# Project Title")
        assert result["category"] == "docs"
        assert "documentation" in result["reason"].lower()

    def test_implementation_file_categorization(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that implementation files are correctly categorized"""
        # Test with implementation file
        result = file_analyzer.categorize_file(
            "service.py",
            "class UserService:\n    def create_user(self, name): return User(name)",
        )

        assert result["category"] == "implementation"
        assert result["requires_strict_security"] is True
        assert "implementation" in result["reason"].lower()

    def test_content_based_categorization(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that content-based categorization works correctly"""
        # Python file with class should be implementation
        result = file_analyzer.categorize_file("service.py", "class UserService: pass")
        assert result["category"] == "implementation"
        assert result["requires_strict_security"] is True

    def test_fast_path_performance(self, file_analyzer: FileContextAnalyzer) -> None:
        """Test that fast path categorization is fast"""
        test_files = [
            "test_user.py",
            "README.md",
            "package.json",
            "__init__.py",
            "data.csv",
            "generated.pb.go",
        ]

        start = time.time()
        for _ in range(1000):  # Run 1000 iterations
            for file_path in test_files:
                file_analyzer.categorize_file(file_path)
        elapsed = time.time() - start

        # Should be very fast - less than 0.1 seconds for 6000 categorizations
        assert elapsed < 0.1, f"Fast path too slow: {elapsed:.3f}s"

    def test_template_file_categorization(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that template files are correctly categorized"""
        template_files = [
            ("index.html", "template"),  # HTML files detected as template
            ("template.jinja2", "template"),  # Jinja2 templates
            ("email.html.erb", "template"),  # ERB templates
            ("view.blade.php", "template"),  # Blade templates (PHP has .php extension)
            ("component.vue", "template"),  # Vue components
            (
                "page.jsx",
                "implementation",
            ),  # JSX could have logic, categorized as implementation
        ]

        for file_path, expected_category in template_files:
            result = file_analyzer.categorize_file(file_path)
            assert (
                result["category"] == expected_category
            ), f"Failed for {file_path}: expected {expected_category}, got {result['category']}"

    def test_migration_file_categorization(
        self, file_analyzer: FileContextAnalyzer
    ) -> None:
        """Test that migration files are categorized appropriately"""
        migration_files = [
            (
                "001_create_users.rb",
                "implementation",
            ),  # Ruby files categorized as implementation
            ("20240101_add_column.sql", "data"),  # SQL files categorized as data
            (
                "migrations/001_initial.py",
                "implementation",
            ),  # Python files default to implementation
            ("db/migrate/create_tables.sql", "data"),  # SQL files categorized as data
        ]

        for file_path, expected_category in migration_files:
            result = file_analyzer.categorize_file(file_path)
            assert (
                result["category"] == expected_category
            ), f"Failed for {file_path}, expected {expected_category}, got {result['category']}"
