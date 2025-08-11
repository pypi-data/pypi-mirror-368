#!/bin/bash

set -e

HOOKS_DIR=".git/hooks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing git hooks..."

cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash

set -e

echo "Running pre-push checks..."

REMOTE="$1"
URL="$2"

BASE_BRANCH="main"
if git rev-parse --verify origin/main >/dev/null 2>&1; then
    BASE_BRANCH="origin/main"
fi

CHANGES=$(git diff --name-only "$BASE_BRANCH"...HEAD 2>/dev/null || echo "")

if [ -z "$CHANGES" ]; then
    echo "No changes detected"
    exit 0
fi

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

SIGNIFICANT_CHANGES=false
for file in $CHANGES; do
    if [[ "$file" == *.py ]] || [[ "$file" == *.sh ]] || [[ "$file" == *.md ]]; then
        if [[ "$file" != "README.md" ]] && [[ "$file" != "CLAUDE.md" ]] && [[ "$file" != "CHANGELOG.md" ]]; then
            SIGNIFICANT_CHANGES=true
            break
        fi
    fi
done

DOCS_UPDATED=false
if [ "$README_CHANGED" = true ] || [ "$CLAUDE_CHANGED" = true ] || [ "$CHANGELOG_CHANGED" = true ]; then
    DOCS_UPDATED=true
fi

if [ "$SIGNIFICANT_CHANGES" = true ] && [ "$DOCS_UPDATED" = false ]; then
    echo "⚠️  WARNING: Significant changes detected but no documentation updated"
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
    read -p "Push without updating documentation? (y/N) " -n 1 -r < /dev/tty
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Push cancelled. Please update README.md, CLAUDE.md, and/or CHANGELOG.md as necessary."
        exit 1
    fi
fi

echo "Pre-push checks passed."
exit 0
EOF

chmod +x "$HOOKS_DIR/pre-push"
echo "✅ Installed pre-push hook"

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The pre-push hook will:"
echo "  - Check if README.md, CLAUDE.md, or CHANGELOG.md are updated when significant changes are made"
echo "  - Prompt for confirmation if no documentation files are updated"
echo ""
echo "To bypass the hook (not recommended), use: git push --no-verify"
