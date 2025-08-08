#!/bin/bash
set -e

echo "Comprehensive Validation Test Suite"
echo "==================================="
echo "This script runs comprehensive validation tests with GEMINI_API_KEY"
echo ""

if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: Skipping comprehensive tests (no GEMINI_API_KEY)"
    exit 0
fi

echo "Running comprehensive validation tests..."
echo "This may take 3-5 minutes due to LLM calls"
echo ""

uv run python tests/test_comprehensive_validation.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ All comprehensive tests passed!"
else
    echo ""
    echo "❌ Some tests failed. Please review the output above."
fi

exit $exit_code
