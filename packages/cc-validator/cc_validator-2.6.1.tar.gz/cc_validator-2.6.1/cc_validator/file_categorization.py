#!/usr/bin/env python3

import os
from typing import Dict, Any, AsyncIterable
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

try:
    from genai_processors import processor, content_api
except ImportError:
    processor = None
    content_api = None


@dataclass_json
@dataclass(frozen=True)
class FileCategoryRequest:
    """Request for file categorization using canonical patterns."""

    file_path: str
    content: str = ""


@dataclass_json
@dataclass(frozen=True)
class FileCategoryResult:
    """File categorization result using canonical patterns."""

    category: str
    is_test_file: bool
    requires_strict_security: bool
    reason: str
    file_path: str = ""


@dataclass_json
@dataclass(frozen=True)
class TestSecretPatternsResult:
    """Test secret patterns result using canonical patterns."""

    patterns: list[str] = field(default_factory=list)


if processor and content_api:

    @processor.part_processor_function
    async def categorize_file_processor(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
        """Canonical file categorization processor using genai-processors patterns."""
        if not content_api.is_dataclass(part, FileCategoryRequest):
            yield content_api.ProcessorPart.from_dataclass(
                FileCategoryResult(
                    category="unknown",
                    is_test_file=False,
                    requires_strict_security=True,
                    reason="Invalid categorization request",
                )
            )
            return

        request = part.get_dataclass(FileCategoryRequest)
        result = FileContextAnalyzer.categorize_file(request.file_path, request.content)

        yield content_api.ProcessorPart.from_dataclass(
            FileCategoryResult(
                category=result["category"],
                is_test_file=result["is_test_file"],
                requires_strict_security=result["requires_strict_security"],
                reason=result["reason"],
                file_path=request.file_path,
            )
        )

    @processor.part_processor_function
    async def test_secret_patterns_processor(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
        """Get test secret patterns using canonical genai-processors patterns."""
        patterns = FileContextAnalyzer.get_test_secret_patterns()
        yield content_api.ProcessorPart.from_dataclass(
            TestSecretPatternsResult(patterns=patterns)
        )


class FileContextAnalyzer:
    """
    Shared file categorization utility for context-aware validation.

    Distinguishes between test files, structural files, config files, and implementation files
    to enable different validation rules based on file context.
    """

    @staticmethod
    def is_test_file(file_path: str, content: str = "") -> bool:
        """
        Determine if a file is a test file based on path patterns and content.

        Test files should have more lenient security validation to allow
        hardcoded test fixtures and mock values.
        """
        if not file_path:
            return False

        # Path-based test file detection
        test_path_patterns = [
            "spec",
            "_test.",
            ".test.",
            "tests/",
            "/test/",
            "\\test\\",
            "/tests/",
            "\\tests\\",
            "conftest.py",
            "test_",
            "_test",
            ".spec.",
        ]

        file_path_lower = file_path.lower()
        for pattern in test_path_patterns:
            if pattern in file_path_lower:
                return True

        # Content-based test detection
        if content:
            test_content_patterns = [
                "def test_",
                "class Test",
                "import unittest",
                "import pytest",
                "test(",
                "describe(",
                "it(",
                "expect(",
                "func Test",
                "@Test",
                "@pytest",
                "assert",
                "assertEqual",
            ]
            for pattern in test_content_patterns:
                if pattern in content:
                    return True

        return False

    @staticmethod
    def is_structural_file(file_path: str, content: str = "") -> bool:
        """
        Determine if a file is structural (setup/configuration) vs implementation.

        Structural files typically don't need strict validation as they contain
        boilerplate, imports, or configuration rather than business logic.
        """
        if not file_path:
            return False

        basename = os.path.basename(file_path)

        # Known structural files by name
        structural_files = {
            "__init__.py",
            "__main__.py",
            "conftest.py",
            "_version.py",
            "version.py",
            "constants.py",
            "index.js",
            "index.ts",
            "mod.rs",
            "lib.rs",
            "main.rs",
            "package-info.java",
            "doc.go",
            "urls.py",
            "apps.py",
            "settings.py",
        }

        if basename in structural_files:
            # Verify it's actually structural by content analysis
            if not FileContextAnalyzer._has_implementation_logic(content):
                return True

        return False

    @staticmethod
    def is_config_file(file_path: str) -> bool:
        """Check if file is a configuration file (no validation needed)"""
        if not file_path:
            return False

        basename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # Configuration file extensions (including infrastructure-as-code)
        config_extensions = {
            ".ini",
            ".toml",
            ".yaml",
            ".yml",
            ".json",
            ".cfg",
            ".conf",
            ".tf",
            ".tfvars",
            ".hcl",
        }
        if ext in config_extensions:
            return True

        # Configuration file names
        config_names = {
            "setup.py",
            "pyproject.toml",
            "Dockerfile",
            "Makefile",
            "docker-compose.yml",
            "docker-compose.yaml",
            ".env.example",
            ".gitignore",
            ".gitattributes",
            "tox.ini",
            "pytest.ini",
            "mypy.ini",
            ".flake8",
            ".pylintrc",
            "jest.config.js",
        }

        return basename in config_names

    @staticmethod
    def is_template_file(file_path: str) -> bool:
        """
        Determine if a file is a template file (HTML, Jinja2, etc.)

        Template files should have template-appropriate validation focusing on
        XSS prevention and escaping rather than code-level security.
        """
        if not file_path:
            return False

        ext = os.path.splitext(file_path)[1].lower()

        # Template file extensions
        template_extensions = {
            ".html",
            ".htm",  # HTML templates
            ".jinja",
            ".jinja2",
            ".j2",  # Jinja2 templates
            ".tpl",
            ".tmpl",  # Generic templates
            ".hbs",
            ".handlebars",  # Handlebars
            ".ejs",  # Embedded JavaScript
            ".pug",
            ".jade",  # Pug/Jade
            ".mustache",  # Mustache
            ".liquid",  # Liquid
            ".erb",  # Ruby ERB
            ".php",  # PHP templates
            ".twig",  # Twig
            ".vue",  # Vue single-file components
            ".svelte",  # Svelte components
        }

        if ext in template_extensions:
            return True

        # Check for template directories
        template_dirs = ["templates", "views", "layouts", "partials", "components"]
        path_parts = file_path.lower().split(os.sep)
        return any(part in template_dirs for part in path_parts)

    @staticmethod
    def categorize_file(file_path: str, content: str = "") -> Dict[str, Any]:
        """
        Categorize a file for context-aware validation.

        Returns:
            {
                'category': 'test' | 'structural' | 'config' | 'docs' | 'data' | 'template' | 'implementation',
                'is_test_file': bool,
                'requires_strict_security': bool,
                'reason': str
            }
        """
        if not file_path:
            return {
                "category": "unknown",
                "is_test_file": False,
                "requires_strict_security": True,
                "reason": "No file path provided",
            }

        basename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # Test files - allow lenient security for test fixtures
        if FileContextAnalyzer.is_test_file(file_path, content):
            return {
                "category": "test",
                "is_test_file": True,
                "requires_strict_security": False,
                "reason": "Test file - lenient validation for fixtures",
            }

        # Lock files - check before config files to avoid JSON extension collision
        lock_files = {
            "pnpm-lock.yaml",
            "poetry.lock",
            "Pipfile.lock",
            "composer.lock",
        }
        if basename in lock_files:
            return {
                "category": "data",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Dependency lock file",
            }

        # Configuration files - minimal security validation
        if FileContextAnalyzer.is_config_file(file_path):
            return {
                "category": "config",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Configuration file",
            }

        # Documentation files - no security validation needed
        if ext in [".md", ".rst", ".txt", ".adoc"] or "README" in basename:
            return {
                "category": "docs",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Documentation file",
            }

        # Template files - template-specific validation
        if FileContextAnalyzer.is_template_file(file_path):
            return {
                "category": "template",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Template file - focus on XSS prevention",
            }

        # Data/schema files - minimal validation
        schema_extensions = {".proto", ".graphql", ".sql", ".avsc", ".xsd", ".wsdl"}
        if ext in schema_extensions:
            return {
                "category": "data",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Schema/data definition file",
            }

        # Structural files - minimal validation
        if FileContextAnalyzer.is_structural_file(file_path, content):
            return {
                "category": "structural",
                "is_test_file": False,
                "requires_strict_security": False,
                "reason": "Structural file with minimal logic",
            }

        # Default: implementation files need strict security validation
        return {
            "category": "implementation",
            "is_test_file": False,
            "requires_strict_security": True,
            "reason": "Implementation file requiring strict validation",
        }

    @staticmethod
    def _has_implementation_logic(content: str) -> bool:
        """Check if content contains actual implementation logic vs just imports/setup"""
        if not content.strip():
            return False

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in lines:
            # Skip comments and docstrings
            if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                continue
            # Skip simple imports and metadata
            if line.startswith(
                ("import ", "from ", "__version__", "__author__", "__email__")
            ):
                continue
            # Skip simple variable assignments
            if any(
                line.startswith(var)
                for var in ["__all__", "__version__", "__author__", "__email__"]
            ):
                continue
            # Check for actual implementation patterns
            if any(
                keyword in line
                for keyword in [
                    "def ",
                    "class ",
                    "if ",
                    "for ",
                    "while ",
                    "try:",
                    "except",
                    "return ",
                    "yield ",
                    "async ",
                    "await ",
                ]
            ):
                return True

        return False

    @staticmethod
    def get_test_secret_patterns() -> list[str]:
        """
        Get list of acceptable test secret patterns for lenient validation.

        These patterns are allowed in test files but would be blocked in production code.
        """
        return [
            r"test[_-]",  # test_, test-
            r"mock[_-]",  # mock_, mock-
            r"dummy[_-]",  # dummy_, dummy-
            r"fake[_-]",  # fake_, fake-
            r"example[_-]",  # example_, example-
            r"sample[_-]",  # sample_, sample-
            r"placeholder[_-]",  # placeholder_, placeholder-
        ]
