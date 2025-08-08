#!/usr/bin/env python3

import abc
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class RunResult:
    """Standardized test result format for all languages"""

    def __init__(self) -> None:
        self.timestamp = time.time()
        self.status = "unknown"
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0
        self.duration = 0.0
        self.passes: List[Dict[str, Any]] = []
        self.failures: List[Dict[str, Any]] = []
        self.errors_list: List[Dict[str, Any]] = []
        self.skipped_list: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to standardized dictionary format"""
        return {
            "timestamp": self.timestamp,
            "status": self.status,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "duration": self.duration,
            "passes": self.passes,
            "failures": self.failures,
            "errors_list": self.errors_list,
            "skipped_list": self.skipped_list,
        }


class BaseTestReporter(abc.ABC):
    """Abstract base class for language-specific test reporters"""

    def __init__(self, data_dir: str = ".claude/cc-validator/data"):
        self.data_dir = Path(data_dir)
        self.test_result = RunResult()

    def store_results(self, test_result: RunResult) -> None:
        """Store test results in FileStorage-compatible format"""
        current_time = time.time()

        stored_data = {
            "timestamp": current_time,
            "expiry": current_time + (20 * 60),  # 20 minutes from now
            "test_results": test_result.to_dict(),
        }

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        test_file = self.data_dir / "test.json"

        try:
            # Atomic write using temporary file
            temp_file = test_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(stored_data, f, indent=2)
            temp_file.replace(test_file)

            self._print_results_summary(test_result)

        except Exception as e:
            print(f"WARNING: Failed to store test results: {e}")

    def _print_results_summary(self, test_result: RunResult) -> None:
        """Print test results summary"""
        print(
            f"Test results captured for TDD validation: {test_result.total_tests} tests"
        )
        print(
            f"   Passed: {test_result.passed}, Failed: {test_result.failed}, Skipped: {test_result.skipped}"
        )

    @abc.abstractmethod
    def parse_test_output(self, output: str) -> RunResult:
        """Parse language-specific test output into standardized format"""
        pass

    @abc.abstractmethod
    def get_language_name(self) -> str:
        """Return the language name for this reporter"""
        pass


class PythonTestReporter(BaseTestReporter):
    """Python pytest test reporter (extends the existing pytest plugin)"""

    def get_language_name(self) -> str:
        return "Python"

    def parse_test_output(self, output: str) -> RunResult:
        """Parse pytest JSON output"""
        # This is handled by the pytest plugin directly
        # This method is for manual integration scenarios
        try:
            data = json.loads(output)
            result = RunResult()

            if "summary" in data:
                summary = data["summary"]
                result.total_tests = summary.get("total", 0)
                result.passed = summary.get("passed", 0)
                result.failed = summary.get("failed", 0)
                result.skipped = summary.get("skipped", 0)

            result.status = (
                "failed"
                if result.failed > 0
                else "passed" if result.passed > 0 else "no_tests"
            )
            return result

        except json.JSONDecodeError:
            # Fallback for plain text output
            result = RunResult()
            result.status = "no_tests"
            return result


class TypeScriptTestReporter(BaseTestReporter):
    """TypeScript/JavaScript Jest/Vitest test reporter"""

    def get_language_name(self) -> str:
        return "TypeScript/JavaScript"

    def parse_test_output(self, output: str) -> RunResult:
        """Parse Jest/Vitest JSON output"""
        try:
            data = json.loads(output)
            result = RunResult()

            # Jest format
            if "numTotalTests" in data:
                result.total_tests = data.get("numTotalTests", 0)
                result.passed = data.get("numPassedTests", 0)
                result.failed = data.get("numFailedTests", 0)
                result.skipped = data.get("numPendingTests", 0)

                # Parse test results
                for test_result in data.get("testResults", []):
                    for assertion in test_result.get("assertionResults", []):
                        test_info = {
                            "test": assertion.get("title", ""),
                            "file": test_result.get("name", ""),
                            "duration": assertion.get("duration", 0)
                            / 1000,  # Convert ms to seconds
                        }

                        if assertion.get("status") == "passed":
                            result.passes.append(test_info)
                        elif assertion.get("status") == "failed":
                            test_info["error"] = assertion.get(
                                "failureMessages", ["Unknown failure"]
                            )[0]
                            result.failures.append(test_info)

            result.status = (
                "failed"
                if result.failed > 0
                else "passed" if result.passed > 0 else "no_tests"
            )
            return result

        except json.JSONDecodeError:
            result = RunResult()
            result.status = "no_tests"
            return result


class GoTestReporter(BaseTestReporter):
    """Go test reporter"""

    def get_language_name(self) -> str:
        return "Go"

    def parse_test_output(self, output: str) -> RunResult:
        """Parse Go test JSON output"""
        try:
            lines = output.strip().split("\n")
            result = RunResult()

            for line in lines:
                if not line.strip():
                    continue

                data = json.loads(line)
                action = data.get("Action", "")
                test_name = data.get("Test", "")
                package = data.get("Package", "")

                if action == "pass" and test_name:
                    result.passed += 1
                    result.passes.append(
                        {
                            "test": test_name,
                            "file": package,
                            "duration": data.get("Elapsed", 0),
                        }
                    )
                elif action == "fail" and test_name:
                    result.failed += 1
                    result.failures.append(
                        {
                            "test": test_name,
                            "file": package,
                            "error": data.get("Output", "Test failed"),
                            "duration": data.get("Elapsed", 0),
                        }
                    )
                elif action == "skip" and test_name:
                    result.skipped += 1
                    result.skipped_list.append(
                        {
                            "test": test_name,
                            "file": package,
                            "reason": data.get("Output", "Skipped"),
                        }
                    )

            result.total_tests = result.passed + result.failed + result.skipped
            result.status = (
                "failed"
                if result.failed > 0
                else "passed" if result.passed > 0 else "no_tests"
            )
            return result

        except json.JSONDecodeError:
            result = RunResult()
            result.status = "no_tests"
            return result


class RustTestReporter(BaseTestReporter):
    """Rust cargo test reporter"""

    def get_language_name(self) -> str:
        return "Rust"

    def parse_test_output(self, output: str) -> RunResult:
        """Parse Rust cargo test JSON output"""
        try:
            lines = output.strip().split("\n")
            result = RunResult()

            for line in lines:
                if not line.strip():
                    continue

                data = json.loads(line)

                if data.get("type") == "test":
                    test_name = data.get("name", "")
                    event = data.get("event", "")

                    if event == "ok":
                        result.passed += 1
                        result.passes.append(
                            {
                                "test": test_name,
                                "file": "",  # Rust doesn't always provide file info
                                "duration": data.get("exec_time", 0),
                            }
                        )
                    elif event == "failed":
                        result.failed += 1
                        result.failures.append(
                            {
                                "test": test_name,
                                "file": "",
                                "error": data.get("stdout", "Test failed"),
                            }
                        )
                    elif event == "ignored":
                        result.skipped += 1
                        result.skipped_list.append(
                            {
                                "test": test_name,
                                "file": "",
                                "reason": "Ignored",
                            }
                        )

            result.total_tests = result.passed + result.failed + result.skipped
            result.status = (
                "failed"
                if result.failed > 0
                else "passed" if result.passed > 0 else "no_tests"
            )
            return result

        except json.JSONDecodeError:
            result = RunResult()
            result.status = "no_tests"
            return result


class DartTestReporter(BaseTestReporter):
    """Dart/Flutter test reporter"""

    def get_language_name(self) -> str:
        return "Dart/Flutter"

    def parse_test_output(self, output: str) -> RunResult:
        """Parse Dart/Flutter test JSON output"""
        try:
            lines = output.strip().split("\n")
            result = RunResult()

            for line in lines:
                if not line.strip():
                    continue

                data = json.loads(line)
                event_type = data.get("type", "")

                if event_type == "testDone":
                    test_name = data.get("test", {}).get("name", "")
                    test_result = data.get("result", "")

                    if test_result == "success":
                        result.passed += 1
                        result.passes.append(
                            {
                                "test": test_name,
                                "file": data.get("test", {}).get("url", ""),
                                "duration": data.get("time", 0)
                                / 1000,  # Convert ms to seconds
                            }
                        )
                    elif test_result == "failure":
                        result.failed += 1
                        result.failures.append(
                            {
                                "test": test_name,
                                "file": data.get("test", {}).get("url", ""),
                                "error": data.get("error", "Test failed"),
                            }
                        )
                    elif test_result == "skipped":
                        result.skipped += 1
                        result.skipped_list.append(
                            {
                                "test": test_name,
                                "file": data.get("test", {}).get("url", ""),
                                "reason": "Skipped",
                            }
                        )

            result.total_tests = result.passed + result.failed + result.skipped
            result.status = (
                "failed"
                if result.failed > 0
                else "passed" if result.passed > 0 else "no_tests"
            )
            return result

        except json.JSONDecodeError:
            result = RunResult()
            result.status = "no_tests"
            return result


# Registry of available test reporters
TEST_REPORTERS = {
    "python": PythonTestReporter,
    "typescript": TypeScriptTestReporter,
    "javascript": TypeScriptTestReporter,  # Same as TypeScript
    "go": GoTestReporter,
    "rust": RustTestReporter,
    "dart": DartTestReporter,
    "flutter": DartTestReporter,  # Same as Dart
}


def get_test_reporter(
    language: str, data_dir: str = ".claude/cc-validator/data"
) -> Optional[BaseTestReporter]:
    """Get test reporter for specified language"""
    if not language:
        return None
    reporter_class = TEST_REPORTERS.get(language.lower())
    if reporter_class:
        return reporter_class(data_dir)  # type: ignore[abstract]
    return None


def store_manual_test_results(
    test_output: str, language: str, data_dir: str = ".claude/cc-validator/data"
) -> bool:
    """Manually store test results from command output"""
    reporter = get_test_reporter(language, data_dir)
    if not reporter:
        print(f"WARNING: No test reporter available for language: {language}")
        return False

    try:
        test_result = reporter.parse_test_output(test_output)
        reporter.store_results(test_result)
        return True
    except Exception as e:
        print(f"WARNING: Failed to parse {language} test output: {e}")
        return False
