#!/bin/bash

set -e

echo "Checking if documentation has been updated..."

BASE_BRANCH="${1:-main}"

CHANGES=$(git diff --name-only "$BASE_BRANCH"...HEAD 2>/dev/null || git diff --name-only --staged)

README_CHANGED=false
CLAUDE_CHANGED=false
CHANGELOG_CHANGED=false

if echo "$CHANGES" | grep -q "^README.md$"; then
    README_CHANGED=true
fi

if echo "$CHANGES" | grep -q "^CLAUDE.md$"; then
    CLAUDE_CHANGED=true
fi

if echo "$CHANGES" | grep -q "^CHANGELOG.md$"; then
    CHANGELOG_CHANGED=true
fi

DOCS_CHANGED_COUNT=0
if [ "$README_CHANGED" = true ]; then
    ((DOCS_CHANGED_COUNT++))
fi
if [ "$CLAUDE_CHANGED" = true ]; then
    ((DOCS_CHANGED_COUNT++))
fi
if [ "$CHANGELOG_CHANGED" = true ]; then
    ((DOCS_CHANGED_COUNT++))
fi

if [ "$DOCS_CHANGED_COUNT" -eq 3 ]; then
    echo "✅ All documentation files have been updated (README.md, CLAUDE.md, and CHANGELOG.md)"
    exit 0
elif [ "$DOCS_CHANGED_COUNT" -eq 2 ]; then
    echo "✅ Two documentation files have been updated"
    if [ "$README_CHANGED" = false ]; then
        echo "⚠️  Note: README.md was not updated - consider if it needs updates"
    fi
    if [ "$CLAUDE_CHANGED" = false ]; then
        echo "⚠️  Note: CLAUDE.md was not updated - consider if it needs updates"
    fi
    if [ "$CHANGELOG_CHANGED" = false ]; then
        echo "⚠️  Note: CHANGELOG.md was not updated - consider if it needs updates"
    fi
    exit 0
elif [ "$DOCS_CHANGED_COUNT" -eq 1 ]; then
    echo "✅ One documentation file has been updated"
    echo "⚠️  Consider updating other documentation files:"
    if [ "$README_CHANGED" = false ]; then
        echo "   - README.md for user-facing changes"
    fi
    if [ "$CLAUDE_CHANGED" = false ]; then
        echo "   - CLAUDE.md for Claude Code usage changes"
    fi
    if [ "$CHANGELOG_CHANGED" = false ]; then
        echo "   - CHANGELOG.md for version history"
    fi
    exit 0
else
    echo "⚠️  WARNING: No documentation files have been modified"
    echo ""
    echo "Changed files:"
    echo "$CHANGES" | sed 's/^/  - /'
    echo ""
    echo "Consider updating documentation if your changes:"
    echo "  - Add new features or functionality (update README.md and CHANGELOG.md)"
    echo "  - Change installation or usage instructions (update README.md)"
    echo "  - Modify configuration options (update README.md)"
    echo "  - Update dependencies or requirements (update README.md)"
    echo "  - Affect Claude Code usage patterns (update CLAUDE.md)"
    echo "  - Include bug fixes or improvements (update CHANGELOG.md)"
    echo ""
    read -p "Do you want to continue without updating documentation? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Continuing without documentation changes..."
        exit 0
    else
        echo "Aborting. Please update README.md, CLAUDE.md, and/or CHANGELOG.md as necessary."
        exit 1
    fi
fi
