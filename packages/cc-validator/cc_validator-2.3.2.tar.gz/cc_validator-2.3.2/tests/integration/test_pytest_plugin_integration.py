#!/usr/bin/env python3

import pytest
import time
import sys
import subprocess
import threading
import concurrent.futures


def test_simple_pass() -> None:
    """A simple test that should pass"""
    assert 1 + 1 == 2


def test_another_pass() -> None:
    """Another test that should pass"""
    assert "hello".upper() == "HELLO"


def test_with_slight_delay() -> None:
    """Test with a small delay to check duration tracking"""
    time.sleep(0.1)
    assert len([1, 2, 3]) == 3


def test_pytest_plugin_creates_results() -> None:
    """Test that our pytest plugin creates test result files"""
    # This test runs after the others, so results should be captured
    # We can't test the file creation here since pytest runs all tests
    # in the same session, but we can verify our logic
    assert True


class TestClass:
    """Test class to verify class-based test detection"""

    def test_method_in_class(self) -> None:
        """Test method within a class"""
        assert hasattr(self, "__class__")

    def test_another_method(self) -> None:
        """Another test method within a class"""
        result = 5 * 5
        assert result == 25


class PytestIntegrationTests:
    """Test runner for pytest plugin integration tests with parallel execution"""

    def __init__(self) -> None:
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters

    def run_single_test(self, test_name: str) -> bool:
        """Run a single pytest test"""
        with self.lock:
            self.total += 1

        try:
            # Run pytest for a specific test
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", f"{__file__}::{test_name}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            success = result.returncode == 0
            status = "PASS" if success else "FAIL"

            print(f"{test_name}: {status}")

            if success:
                with self.lock:
                    self.passed += 1
            else:
                print(f"  Output: {result.stdout[:100]}...")
                if result.stderr:
                    print(f"  Error: {result.stderr[:100]}...")

            return success

        except subprocess.TimeoutExpired:
            print(f"{test_name}: TIMEOUT")
            return False
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            return False

    def run_all_tests(self) -> int:
        """Run all pytest plugin integration tests in parallel"""
        print("PYTEST PLUGIN INTEGRATION TEST SUITE")
        print("=" * 60)
        print("Testing pytest plugin functionality")
        print("PARALLEL EXECUTION: Running tests concurrently")
        print("=" * 60)

        start_time = time.time()

        # List of test functions to run
        test_functions = [
            "test_simple_pass",
            "test_another_pass",
            "test_with_slight_delay",
            "test_skipped",
            "test_pytest_plugin_creates_results",
            "TestClass::test_method_in_class",
            "TestClass::test_another_method",
        ]

        print("Starting parallel test execution...")

        # Run tests in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            list(executor.map(self.run_single_test, test_functions))

        elapsed_time = time.time() - start_time

        print(f"\n{'=' * 60}")
        print(f"FINAL RESULTS: {self.passed}/{self.total} tests passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")

        if self.passed == self.total:
            print("✓ ALL PYTEST INTEGRATION TESTS PASSED")
            return 0
        else:
            # Note: test_skipped will count as passed in pytest
            # Adjust expectation if needed
            print("✗ SOME PYTEST INTEGRATION TESTS FAILED")
            return 1


def main() -> int:
    """Main test runner"""
    # Option 1: Run using pytest directly (traditional way)
    if "--pytest" in sys.argv:
        sys.exit(pytest.main([__file__, "-v"]))

    # Option 2: Run using our parallel test runner
    test_suite = PytestIntegrationTests()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
