"""
CC-Validator (Claude Code Validator)

Hybrid security + TDD validation for Claude Code tool execution using Google Gemini and ADK-inspired patterns.
"""

__version__ = "2.4.0"
__author__ = "Jihun Kim"
__email__ = "jihunkim0@noreply.github.com"

from .canonical_pipeline import CanonicalPipelineValidator
from .file_storage import FileStorage
from .file_categorization import FileContextAnalyzer
from .pytest_plugin import PytestReporter
from .reporters import (
    BaseTestReporter,
    RunResult,
    PythonTestReporter,
    TypeScriptTestReporter,
    GoTestReporter,
    RustTestReporter,
    DartTestReporter,
    get_test_reporter,
    store_manual_test_results,
)

__all__ = [
    "CanonicalPipelineValidator",  # Main canonical pipeline validation
    "FileStorage",  # Context persistence
    "FileContextAnalyzer",  # Shared file categorization utility
    "PytestReporter",  # Automatic pytest result capture
    "BaseTestReporter",  # Base class for test reporters
    "RunResult",  # Standardized test result format
    "PythonTestReporter",  # Python test result parsing
    "TypeScriptTestReporter",  # TypeScript/JavaScript test parsing
    "GoTestReporter",  # Go test result parsing
    "RustTestReporter",  # Rust test result parsing
    "DartTestReporter",  # Dart/Flutter test parsing
    "get_test_reporter",  # Get reporter by language
    "store_manual_test_results",  # Manual test result storage
]
