#!/usr/bin/env python3

from typing import Dict, List, Any
import json


class TDDCorePrompt:
    """Core TDD principles and Red-Green-Refactor cycle enforcement rules"""

    @staticmethod
    def get_tdd_principles() -> str:
        return """
# TDD PRINCIPLES

**CORE RULE**: ONE new test per operation only.

1. **RED**: Write ONE failing test for desired behavior
2. **GREEN**: Write MINIMAL code to pass the test
3. **REFACTOR**: Improve code while keeping tests green

## VALIDATION RULES

**BLOCK IF:**
- Multiple NEW tests in one operation (NET increase > 1)
- Code contains comments
- Implementation beyond test requirements
- SOLID principles violated

**ALLOW:**
- Modifying existing test implementation (Red phase refinement)
- Renaming test functions (same test count)
- Replacing one test with another (net zero change)
- Simplifying complex tests into focused ones

**ENFORCE:**
- ONE test rule (NET new tests, not modifications)
- Self-evident code (no comments)
- Minimal implementation
- SOLID: SRP, OCP, LSP, ISP, DIP
- Zen: explicit, simple, readable, one obvious way

## TEST EVOLUTION IN TDD

During RED phase, tests naturally evolve as understanding improves:
- **Valid**: Simplifying overly complex test
- **Valid**: Renaming test to better express intent
- **Valid**: Changing test implementation to fix setup
- **Invalid**: Adding multiple new tests at once

## FILE CLASSIFICATION

**SKIP TDD:** Structural files (__init__.py, configs, docs)
**REQUIRE TDD:** Implementation files with logic
**SPECIAL RULES:** Test files (ONE test rule still applies)
"""


class EditAnalysisPrompt:
    """Analysis prompt for Edit operations - ported from TDD Guard's edit-analysis.ts"""

    @staticmethod
    def get_analysis_prompt(old_content: str, new_content: str, file_path: str) -> str:
        return f"""
# EDIT ANALYSIS

FILE: {file_path}

OLD:
```
{old_content}
```

NEW:
```
{new_content}
```

VALIDATE:
1. Count new tests (only ONE allowed)
2. Check for comments (NONE allowed)
3. Verify minimal implementation
4. Ensure SOLID compliance
5. Zen of Python adherence

DECISION: Block if TDD/quality rules violated.
"""


class WriteAnalysisPrompt:
    """Analysis prompt for Write operations - ported from TDD Guard's write-analysis.ts"""

    @staticmethod
    def get_analysis_prompt(file_path: str, content: str) -> str:
        # Handle None or empty file_path safely
        safe_file_path = file_path or ""
        is_test_file = any(
            pattern in safe_file_path.lower()
            for pattern in ["test", "spec", "_test.", ".test.", "tests/"]
        )

        file_type = "TEST FILE" if is_test_file else "IMPLEMENTATION FILE"

        return f"""
# WRITE ANALYSIS

FILE: {file_path} ({file_type})

CONTENT:
```
{content}
```

VALIDATE:
- TEST FILE: Only ONE new test allowed (TDD rule)
- IMPL FILE: Must have failing test first
- NO COMMENTS allowed
- SOLID compliance required
- Zen of Python required
- Minimal implementation only

DECISION: Block if no test exists or rules violated.
"""


class MultiEditAnalysisPrompt:
    """Analysis prompt for MultiEdit operations - ported from TDD Guard's multi-edit-analysis.ts"""

    @staticmethod
    def get_analysis_prompt(edits: List[Dict[str, Any]]) -> str:
        edits_summary = []
        for i, edit in enumerate(edits, 1):
            file_path = edit.get("file_path", f"Edit {i}")
            old_content = (
                edit.get("old_string", "")[:200] + "..."
                if len(edit.get("old_string", "")) > 200
                else edit.get("old_string", "")
            )
            new_content = (
                edit.get("new_string", "")[:200] + "..."
                if len(edit.get("new_string", "")) > 200
                else edit.get("new_string", "")
            )

            edits_summary.append(
                f"""
**EDIT {i}**: {file_path}
OLD: {old_content}
NEW: {new_content}
"""
            )

        return f"""
# MULTIEDIT ANALYSIS

EDITS:
{chr(10).join(edits_summary)}

VALIDATE:
- Total new tests across ALL edits (max ONE)
- NO COMMENTS in any edit
- Minimal implementation
- SOLID compliance
- Zen of Python adherence

DECISION: Block if total new tests > 1 or rules violated.
"""


class TDDContextFormatter:
    """Format test results and context for TDD validation"""

    @staticmethod
    def format_test_output(test_results: Dict[str, Any]) -> str:
        if not test_results:
            return "\n## TEST OUTPUT\nNo recent test results available."

        return f"""
## TEST OUTPUT CONTEXT

### Test Execution Results
**Timestamp**: {test_results.get("timestamp", "Unknown")}
**Status**: {test_results.get("status", "Unknown")}

### Test Failures (guide implementation)
{json.dumps(test_results.get("failures", []), indent=2)}

### Test Passes (avoid over-implementation)
{json.dumps(test_results.get("passes", []), indent=2)}

### Error Messages (inform minimal fixes)
{json.dumps(test_results.get("errors_list", []), indent=2)}

### Collection Errors (fix imports/syntax before tests can run)
{json.dumps(test_results.get("collection_errors", []), indent=2)}

### Collection Errors (import/setup failures requiring implementation)
{json.dumps(test_results.get("collection_errors", []), indent=2)}

### TDD GUIDANCE FROM TEST OUTPUT
- **Red Phase**: Use failures to guide what needs to be implemented
- **Collection Errors**: Import errors indicate missing implementation - write minimal code to satisfy imports
- **Green Phase**: Implement minimal code to make failing tests pass
- **Avoid**: Implementing functionality not required by current failures
- **Focus**: Address specific error messages and assertions
"""

    @staticmethod
    def format_tdd_context(context: Dict[str, Any]) -> str:
        """Format complete TDD context including test results, todos, and modifications"""

        test_section = TDDContextFormatter.format_test_output(
            context.get("test_results") or {}
        )

        todos_section = ""
        if context.get("todos"):
            todos_section = f"""
## TODO CONTEXT
Current todos that may influence TDD decisions:
{json.dumps(context.get("todos"), indent=2)}
"""

        modifications_section = ""
        if context.get("recent_modifications"):
            modifications_section = f"""
## RECENT MODIFICATIONS
File changes that provide context for current operation:
{json.dumps(context.get("recent_modifications"), indent=2)}
"""

        return f"""
# TDD VALIDATION CONTEXT

{test_section}

{todos_section}

{modifications_section}

## TDD STATE ASSESSMENT
- **Has valid test data**: {context.get("has_valid_test_data", False)}
- **Current phase likely**: {"Red" if (context.get("test_results") or {}).get("failures") or (context.get("test_results") or {}).get("collection_errors") or (context.get("test_results") or {}).get("errors", 0) > 0 or (context.get("test_results") or {}).get("status") == "failed" else "Green/Refactor"}
- **Context richness**: {"High" if context.get("test_results") else "Low"}
"""
