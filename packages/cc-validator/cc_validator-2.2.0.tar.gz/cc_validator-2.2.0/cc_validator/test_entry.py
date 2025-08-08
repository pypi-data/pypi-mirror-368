#!/usr/bin/env python3
"""Test entry point for quick validation tests"""

import asyncio
import sys
import json
import os


def main() -> None:
    """Entry point for tests that provides hook data via argument"""
    if len(sys.argv) < 2:
        print("Usage: test_entry.py <json_data>", file=sys.stderr)
        sys.exit(1)

    # Parse JSON from command line argument
    try:
        hook_input = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Invalid JSON input", file=sys.stderr)
        sys.exit(1)

    # Import and run validator
    from .hybrid_validator import HybridValidator

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        error_response = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "❌ GEMINI_API_KEY not configured - blocking operations\n\n→ Set GEMINI_API_KEY environment variable to enable validation",
            }
        }
        print(json.dumps(error_response))
        sys.exit(2)

    # Initialize validator
    validator = HybridValidator(api_key)

    # Extract tool info
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    transcript_path = hook_input.get("transcript_path", "")

    # Extract context
    context = validator.security_validator.extract_conversation_context(transcript_path)

    # Run validation
    result = asyncio.run(validator.validate_tool_use(tool_name, tool_input, context))
    validator.security_validator.cleanup_uploaded_files()

    # Get approval status
    is_approved = result.get("approved", False)

    # Build the decision reason text
    reason_parts = []

    if not is_approved:
        # Add main reason
        reason = result.get("reason", "Operation blocked")
        reason_parts.append(f"❌ {reason}")

        # Add suggestions
        if result.get("suggestions"):
            reason_parts.append("")  # Empty line
            for suggestion in result.get("suggestions", []):
                reason_parts.append(f"→ {suggestion}")

    # Create JSON response for Claude Code hooks
    hook_response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow" if is_approved else "deny",
            "permissionDecisionReason": (
                "\n".join(reason_parts) if reason_parts else "Operation approved"
            ),
        }
    }

    # Output JSON to stdout
    print(json.dumps(hook_response))

    # Exit with appropriate code
    sys.exit(0 if is_approved else 2)


if __name__ == "__main__":
    main()
