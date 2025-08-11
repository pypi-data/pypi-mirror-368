#!/usr/bin/env python3
"""
Main entry point for Claude Code ADK-Inspired Validator.

This module provides the command-line interface for the validator,
allowing it to be used with uvx and as a console script.
"""

import sys
import json
import os
import argparse
import subprocess
import asyncio
from pathlib import Path

from .canonical_pipeline import CanonicalPipelineValidator
from .config import DEFAULT_HOOK_TIMEOUT, ProcessorConfig
from .file_storage import FileStorage
from .reporters import store_manual_test_results
from .cli_formatter import ClaudeCodeHookFormatter


def extract_conversation_context(transcript_path: str) -> str:
    """Simple conversation context extractor for pipeline orchestrator"""
    if not transcript_path or not os.path.exists(transcript_path):
        return ""

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _is_uv_project() -> bool:
    """Check if current directory is a uv project."""
    cwd = Path.cwd()
    return (cwd / "pyproject.toml").exists() and (
        (cwd / "uv.lock").exists() or _has_uv_command()
    )


def _has_uv_command() -> bool:
    """Check if uv command is available."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True, timeout=5)
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def _install_package_as_dev_dependency() -> tuple[bool, str]:
    """Install package as dev dependency in uv project."""
    try:
        result = subprocess.run(
            ["uv", "add", "--dev", "cc-validator"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "Package installed successfully as dev dependency"
        else:
            return False, f"Installation failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except FileNotFoundError:
        return False, "uv command not found"
    except Exception as e:
        return False, f"Installation error: {str(e)}"


def setup_claude_hooks(
    validator_command: str = "uvx cc-validator",
) -> None:
    """Setup Claude Code hooks configuration."""
    claude_dir = Path.cwd() / ".claude"
    settings_file = claude_dir / "settings.local.json"

    # Create .claude directory if it doesn't exist
    claude_dir.mkdir(exist_ok=True)

    # Hook configuration
    hook_config = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|Bash|MultiEdit|Update|TodoWrite",
                    "hooks": [
                        {
                            "type": "command",
                            "command": validator_command,
                            "timeout": DEFAULT_HOOK_TIMEOUT,
                        }
                    ],
                }
            ]
        }
    }

    # Merge with existing configuration if present
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                existing_config = json.load(f)

            # Merge configurations
            if "hooks" in existing_config:
                existing_config["hooks"].update(hook_config["hooks"])
            else:
                existing_config.update(hook_config)

            hook_config = existing_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read existing configuration: {e}")
            print("Creating new configuration...")

    # Write configuration
    try:
        with open(settings_file, "w") as f:
            json.dump(hook_config, f, indent=2)

        print("SUCCESS: Claude Code hooks configured successfully!")
        print(f"Configuration written to: {settings_file}")
        print(f"Hook command: {validator_command}")

        # Try to setup pytest plugin integration
        pytest_setup_success = False
        if _is_uv_project():
            print("\nDetected uv project - setting up pytest plugin integration...")
            install_success, install_message = _install_package_as_dev_dependency()

            if install_success:
                print(f"SUCCESS: {install_message}")
                print("SUCCESS: Pytest plugin integration ready!")
                pytest_setup_success = True
            else:
                print(f"WARNING: {install_message}")
                print("Manual setup required for pytest plugin:")
                print("   uv add --dev cc-validator")
        else:
            print("\nFor pytest plugin integration in non-uv projects:")
            print("   pip install cc-validator")
            print("   # or add to your requirements-dev.txt / pyproject.toml")

        # Provide usage instructions
        print("\nSetup Complete!")
        print("Claude Code hooks: Ready")
        if pytest_setup_success:
            print("Pytest plugin: Ready (run 'pytest' to auto-capture test results)")
        else:
            print("Pytest plugin: Manual installation needed")

        # Check for API key
        if not os.environ.get("GEMINI_API_KEY"):
            print(
                "\nWARNING: Don't forget to set your GEMINI_API_KEY environment variable:"
            )
            print("   export GEMINI_API_KEY='your_gemini_api_key'")

    except IOError as e:
        print(f"ERROR: Error writing configuration: {e}")
        sys.exit(1)


def validate_hook_input() -> None:
    """Main validation function for Claude Code hooks."""
    try:
        # Read hook input from stdin
        stdin_input = sys.stdin.read()
        hook_input = json.loads(stdin_input)
    except json.JSONDecodeError:
        # Output error as JSON for Claude Code
        error_response = ClaudeCodeHookFormatter.format_error_response(
            "Invalid JSON input - allowing operation to proceed", allow_operation=True
        )
        print(json.dumps(error_response))
        sys.exit(0)

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        # Block operations when API key is missing
        error_response = ClaudeCodeHookFormatter.format_error_response(
            "❌ GEMINI_API_KEY not configured - blocking operations\n\n→ Set GEMINI_API_KEY environment variable to enable validation"
        )
        print(json.dumps(error_response))
        sys.exit(2)

    # Initialize canonical validation pipeline with config
    config = ProcessorConfig(api_key=api_key)
    file_storage = FileStorage()
    validator = CanonicalPipelineValidator(file_storage, config)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    transcript_path = hook_input.get("transcript_path", "")

    try:
        # Extract conversation context (simple fallback implementation)
        context = extract_conversation_context(transcript_path)

        # Use async validation method
        validation_result = asyncio.run(
            validator.validate_tool_use_async(tool_name, tool_input, context)
        )

        # Format response using the formatter
        hook_response = ClaudeCodeHookFormatter.format_permission_response(
            validation_result
        )

        # Output JSON to stdout for Claude Code
        print(json.dumps(hook_response))

        # Exit with appropriate code
        is_approved = validation_result.get("approved", False)
        sys.exit(0 if is_approved else 2)

    except Exception as e:
        # Output error as JSON for Claude Code
        error_response = ClaudeCodeHookFormatter.format_error_response(
            f"❌ Validation error: {str(e)}"
        )
        print(json.dumps(error_response))
        sys.exit(2)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Canonical Pipeline Security + TDD Validation Hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup Claude Code hooks configuration
  uvx cc-validator --setup

  # Run as validation hook (used by Claude Code)
  uvx cc-validator < hook_input.json

  # Show version information
  uvx cc-validator --version

  # List supported languages for test capture
  uvx cc-validator --list-languages

  # Capture test results for TDD validation
  npm test --json | uvx cc-validator --capture-test-results typescript
  go test -json ./... | uvx cc-validator --capture-test-results go
  cargo test --message-format json | uvx cc-validator --capture-test-results rust
        """,
    )

    parser.add_argument(
        "--setup", action="store_true", help="Setup Claude Code hooks configuration"
    )

    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )

    parser.add_argument(
        "--validator-command",
        default="uvx cc-validator",
        help="Command to use in hook configuration (default: uvx cc-validator)",
    )

    parser.add_argument(
        "--capture-test-results",
        metavar="LANGUAGE",
        choices=["python", "typescript", "javascript", "go", "rust", "dart", "flutter"],
        help="Capture test results from stdin for specified language",
    )

    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List supported languages for test result capture",
    )

    # Parse arguments
    args = parser.parse_args()

    if args.version:
        from . import __version__

        print(f"cc-validator {__version__}")
        print(
            "Canonical pipeline security + TDD validation for Claude Code tool execution"
        )
        print("Using Google Gemini with parallel processor pipeline orchestration")
        return

    if args.setup:
        print("Setting up Claude Code hooks...")
        setup_claude_hooks(args.validator_command)
        return

    if args.list_languages:
        print("Supported languages for test result capture:")
        print("  - python      (pytest)")
        print("  - typescript  (jest, vitest)")
        print("  - javascript  (jest, vitest)")
        print("  - go          (go test)")
        print("  - rust        (cargo test)")
        print("  - dart        (dart test)")
        print("  - flutter     (flutter test)")
        print("\nUsage examples:")
        print("  npm test --json | uvx cc-validator --capture-test-results typescript")
        print("  go test -json ./... | uvx cc-validator --capture-test-results go")
        print(
            "  cargo test --message-format json | uvx cc-validator --capture-test-results rust"
        )
        return

    if args.capture_test_results:
        # Read test output from stdin
        try:
            test_output = sys.stdin.read()
            if not test_output.strip():
                print("Error: No test output provided via stdin", file=sys.stderr)
                sys.exit(1)

            success = store_manual_test_results(test_output, args.capture_test_results)
            if success:
                print(f"SUCCESS: Test results captured for {args.capture_test_results}")
                sys.exit(0)
            else:
                print(
                    f"ERROR: Failed to capture test results for {args.capture_test_results}",
                    file=sys.stderr,
                )
                sys.exit(1)

        except Exception as e:
            print(f"ERROR: Error capturing test results: {e}", file=sys.stderr)
            sys.exit(1)

    # Default behavior: run as validation hook
    validate_hook_input()


if __name__ == "__main__":
    main()
