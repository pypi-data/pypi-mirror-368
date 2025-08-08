#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running pre-PR checks..."

if ! "$SCRIPT_DIR/check-readme-changes.sh"; then
    echo "Pre-PR checks failed."
    exit 1
fi

echo ""
echo "All checks passed! Creating PR..."
echo ""

gh pr create "$@"
