#!/usr/bin/env python3

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    pytest = None
    HAS_PYTEST = False


class PytestReporter:
    """
    Pytest plugin that automatically captures test results for TDD validation.
    Similar to TDD Guard's PytestReporter but adapted for Claude Code ADK Validator.
    """

    def __init__(self) -> None:
        self.test_results: Dict[str, Any] = {
            "timestamp": None,
            "status": "unknown",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0.0,
            "passes": [],
            "failures": [],
            "errors_list": [],
            "skipped_list": [],
            "collection_errors": [],
        }
        self.start_time: Optional[float] = None
        self.data_dir = Path(".claude/cc-validator/data")

    def pytest_sessionstart(self, session) -> None:  # type: ignore[no-untyped-def]
        """Called after the Session object has been created"""
        self.start_time = time.time()
        self.test_results["timestamp"] = self.start_time

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def pytest_runtest_logreport(self, report) -> None:  # type: ignore[no-untyped-def]
        """Process test reports for each test phase"""
        if (
            report.when == "call"
        ):  # Only process the main test execution, not setup/teardown
            self._process_test_result(report)

    def pytest_collectreport(self, report) -> None:  # type: ignore[no-untyped-def]
        """Process collection reports to catch import errors"""
        if report.failed:
            # Collection failed (e.g., ImportError)
            self.test_results["errors"] += 1
            error_info = {
                "file": str(report.fspath) if hasattr(report, "fspath") else "unknown",
                "error": (
                    str(report.longrepr) if report.longrepr else "Collection failed"
                ),
                "type": "collection_error",
            }
            self.test_results["collection_errors"].append(error_info)
            # Also add to errors_list for compatibility
            self.test_results["errors_list"].append(error_info)

            # Update total_tests to include collection errors
            self.test_results["total_tests"] = (
                self.test_results["passed"]
                + self.test_results["failed"]
                + self.test_results["skipped"]
                + self.test_results["errors"]
            )

    def _process_test_result(self, report) -> None:  # type: ignore[no-untyped-def]
        """Process individual test result"""
        test_name = report.nodeid

        if report.passed:
            self.test_results["passed"] += 1
            self.test_results["passes"].append(
                {
                    "test": test_name,
                    "duration": report.duration,
                    "file": self._extract_file_path(test_name),
                }
            )
        elif report.failed:
            self.test_results["failed"] += 1
            failure_info = {
                "test": test_name,
                "duration": report.duration,
                "file": self._extract_file_path(test_name),
                "error": str(report.longrepr) if report.longrepr else "Unknown failure",
                "line": getattr(report, "lineno", None),
            }
            self.test_results["failures"].append(failure_info)
        elif report.skipped:
            self.test_results["skipped"] += 1
            self.test_results["skipped_list"].append(
                {
                    "test": test_name,
                    "reason": str(report.longrepr) if report.longrepr else "Skipped",
                    "file": self._extract_file_path(test_name),
                }
            )

        self.test_results["total_tests"] = (
            self.test_results["passed"]
            + self.test_results["failed"]
            + self.test_results["skipped"]
            + self.test_results["errors"]
        )

    def pytest_sessionfinish(self, session, exitstatus) -> None:  # type: ignore[no-untyped-def]
        """Called after whole test run finished"""
        if self.start_time:
            self.test_results["duration"] = time.time() - self.start_time

        # Determine overall status
        if self.test_results["failed"] > 0 or self.test_results["errors"] > 0:
            self.test_results["status"] = "failed"
        elif self.test_results["passed"] > 0:
            self.test_results["status"] = "passed"
        else:
            self.test_results["status"] = "no_tests"

        # Store results using the FileStorage format
        self._store_test_results()

    def _extract_file_path(self, nodeid: str) -> str:
        """Extract file path from pytest nodeid"""
        # nodeid format is typically: "path/to/test_file.py::TestClass::test_method"
        if "::" in nodeid:
            return nodeid.split("::")[0]
        return nodeid

    def _store_test_results(self) -> None:
        """Store test results in FileStorage-compatible format"""
        current_time = time.time()

        stored_data = {
            "timestamp": current_time,
            "expiry": current_time + (20 * 60),  # 20 minutes from now
            "test_results": self.test_results,
        }

        test_file = self.data_dir / "test.json"

        try:
            # Atomic write using temporary file
            temp_file = test_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(stored_data, f, indent=2)
            temp_file.replace(test_file)

            print(
                f"Test results captured for TDD validation: {self.test_results['total_tests']} tests"
            )
            print(
                f"   Passed: {self.test_results['passed']}, Failed: {self.test_results['failed']}, Errors: {self.test_results['errors']}, Skipped: {self.test_results['skipped']}"
            )

        except Exception as e:
            print(f"WARNING: Failed to store test results: {e}")


if HAS_PYTEST:

    def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
        """Register the pytest plugin"""
        if not hasattr(config, "_pytest_reporter"):
            config._pytest_reporter = PytestReporter()
            config.pluginmanager.register(
                config._pytest_reporter, "claude_adk_reporter"
            )

    def pytest_unconfigure(config) -> None:  # type: ignore[no-untyped-def]
        """Unregister the pytest plugin"""
        if hasattr(config, "_pytest_reporter"):
            config.pluginmanager.unregister(
                config._pytest_reporter, "claude_adk_reporter"
            )
            delattr(config, "_pytest_reporter")

else:
    # Pytest not available - define dummy functions to prevent import errors
    def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
        pass

    def pytest_unconfigure(config) -> None:  # type: ignore[no-untyped-def]
        pass


# This file exports the plugin functions directly
# pytest automatically discovers and uses them via the entry_points configuration
