#!/usr/bin/env python3
"""
Centralized configuration for Claude Code ADK Validator.
"""

# Model configuration
GEMINI_MODEL = "gemini-2.5-flash"
FILE_CATEGORIZATION_MODEL = "gemini-2.5-flash"
SECRET_VALIDATION_MODEL = "gemini-2.5-flash"

# Thinking budgets for different validation types
SECURITY_THINKING_BUDGET = 24576
TDD_THINKING_BUDGET = 24576
FILE_ANALYSIS_THINKING_BUDGET = 4096
SECRET_VALIDATION_THINKING_BUDGET = 4096

# Validation timeouts (milliseconds)
DEFAULT_HOOK_TIMEOUT = 15000
VALIDATION_TIMEOUT = 15000

# Template validation configuration
STRICT_TEMPLATE_VALIDATION = (
    False  # When True, applies stricter security checks to templates
)

# Branch validation configuration
PROTECTED_BRANCHES = ["main", "master", "production"]
ENFORCE_ISSUE_WORKFLOW = True
ISSUE_BRANCH_PATTERN = r"^(\d+)-(.+)$"
