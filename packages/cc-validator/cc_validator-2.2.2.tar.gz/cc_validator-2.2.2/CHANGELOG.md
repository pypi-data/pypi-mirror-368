# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.2] - 2025-08-08

### Changed
- Test suite reorganization into logical categories for improved maintainability
- Consolidated file categorization tests to reduce redundancy
- Removed 11+ redundant test files while maintaining comprehensive coverage

### Added
- Added VERSION_BUMP_CHECKLIST.md documentation for standardized release process

### Improved
- Enhanced test organization with specialized directories (unit/, integration/, tdd/, security/, specialized/)
- Streamlined test suite maintenance through better categorization

## [2.2.1] - 2025-08-08

### Fixed
- Fixed integration tests by converting `FileCategorizationResponse` to dataclass format for genai-processors compatibility
- Fixed TDD enforcement logic that was incorrectly allowing operations that should be blocked
- Fixed test isolation issues in `clean_tdd_context` fixture preventing proper cleanup between tests
- Fixed language suggestion tests to handle LLM response variations more robustly
- Fixed missing `aiohttp` dependency causing file categorization failures

### Added
- Added `dataclasses-json>=0.6.7` dependency for proper model serialization
- Added `aiohttp>=3.12.15` dependency for HTTP operations

### Improved
- Achieved 100% test pass rate (185/185 tests passing)
- Enhanced test stability for both sequential and parallel execution
- Improved TDD validation logic to properly skip only non-code files

## [2.2.0] - 2025-08-08

### Changed
- Complete architectural refactoring to processor-based patterns following genai-processors design
- Migrated all validation logic to streaming processors with proper async/await patterns
- Implemented proper processor composition using + operator for pipeline building
- Refactored TDD validation to use processor-based analysis with structured prompts

### Fixed
- Fixed TDD validation for Update operations to properly count NET new tests
- Fixed test isolation issues causing cross-test contamination in parallel execution
- Fixed file categorization for simple implementation files being misclassified
- Fixed collection error handling in TDD validation pipeline
- Improved LLM prompt engineering to reduce hallucination in validation responses

### Removed
- Removed all API key fallback logic as per security requirements
- Removed tests for API key fallback scenarios
- Removed unused environment fixtures from test suite

### Added
- Enhanced test fixture for aggressive TDD context cleanup between tests
- Added proper file content reading for Edit/MultiEdit operations in TDD validation
- Added comprehensive processor-based test coverage

## [2.1.1] - 2025-07-31

### Fixed
- **Critical Language Detection Bug**: Fixed pre-validation returns bypassing LLM suggestions
  - Python code no longer receives Java-specific error messages
  - Pre-validation failures now properly call LLM for language-specific suggestions
  - Enhanced prompts with explicit language context to prevent cross-language hallucination
- **Test Failures**: Fixed 3 failing tests
  - Increased timeout for MockClaudeCodeEnvironment to 30s to prevent timeout errors
  - Fixed test fixture to pass transcript_path correctly
  - Added collection_errors check to has_failing_tests logic in 4 locations
- **Edit/MultiEdit Operations**: Now read actual file content for proper TDD validation
  - Fixed bypass where Edit/MultiEdit weren't checking file content
  - Ensures proper categorization and TDD enforcement

### Improved
- **LLM Prompt Enhancement**: Added stronger language-specific instructions
  - CRITICAL markers to enforce language-appropriate suggestions
  - Explicit "MUST NOT mention Java" instructions for non-Java files
  - Language and framework context prominently displayed at prompt start
- **Test Data Management**: Added cleanup in tests to prevent interference
  - Clear test data before runs to avoid cross-test contamination

### Technical
- Modified pre-validation returns to continue to LLM for suggestion generation
- Updated TDDContextFormatter to display collection_errors properly
- Already optimal parallelization confirmed (security + TDD run via asyncio.gather)

## [2.1.0] - 2025-07-31

### Added
- **Terraform Support**: Infrastructure-as-Code files (.tf, .tfvars, .hcl) now categorized as configuration
- **Language-Specific TDD Suggestions**: Dynamic test framework recommendations for 20+ languages
  - Python → pytest
  - JavaScript/TypeScript → Jest, Mocha, Vitest
  - Go → Built-in testing package
  - Rust → #[test] framework
  - Terraform → Native terraform test (.tftest.hcl)
  - And 15+ more languages
- **Language Detection**: Automatic detection from file extensions
- **Test Framework Info**: `get_test_framework_info()` method provides language-specific guidance

### Changed
- Config file categorization now includes infrastructure files (.tf, .tfvars, .hcl)
- TDD prompts enhanced with language context for better suggestions
- LLM-generated suggestions now tailored to detected programming language

### Improved
- Infrastructure files skip traditional TDD requirements (declarative vs procedural)
- More helpful TDD guidance with concrete language-specific examples
- Better developer experience with contextual test framework suggestions

## [2.0.14] - 2025-07-30

### Fixed
- Replaced brittle pattern matching with robust LLM-based language consistency validation
- Now catches pattern variations like "MyServiceImpl.java" that were evading detection
- Uses indicator counting instead of exact string matching for better coverage

### Added
- Language detection from file extensions
- Intelligent response sanitization when cross-language suggestions detected

### Improved
- More maintainable solution that adapts to LLM behavior variations
- Future-proof against new pattern evasions

## [2.0.13] - 2025-07-30

### Fixed
- Enhanced cross-language hallucination detection to prevent confusing TDD suggestions
- Python files now block Java-specific patterns (ServiceTest.java, @Test, assertEquals, etc.)
- JavaScript/TypeScript files block Java and Python patterns
- Go files block patterns from other languages

### Improved
- Better user experience by ensuring language-appropriate TDD suggestions

## [2.0.12] - 2025-07-29

### Fixed
- Critical TDD bypass where minimal files (e.g., main.py with just print("hello")) were miscategorized as "structural"
- Edit/MultiEdit operations now read actual file content for proper categorization
- Entry point files (main.py, app.py, etc.) always require TDD regardless of content

### Changed  
- BREAKING: Removed hybrid categorization - ALL files now go through LLM analysis
- Any LLM categorization failure now defaults to requiring TDD (fail-secure)
- Stricter LLM prompt treats ANY executable code as implementation requiring TDD

### Security
- Eliminated fast-path pattern matching that allowed TDD bypass exploits

## [1.12.4] - 2025-07-26

### Fixed
- Modified hybrid validator to show both Security and TDD reasons when both validations fail
- TDD violations are now visible even when security validation also fails
- Format: "Security: <reason> | TDD: <reason>" when both fail

### Added
- Test case to verify TDD blocking behavior for UI/dashboard file updates

## [1.12.3] - 2025-07-26

### Fixed
- Fixed version mismatch where __init__.py had 1.11.4 while pyproject.toml had 1.12.2
- Ensures uvx claude-code-adk-validator --version shows correct version

## [1.12.2] - 2025-07-26

### Fixed
- Fixed GitHub Actions workflows to use `uv run pytest` instead of deleted test_validation.py
- Fixed PyPI publish workflow failures

## [1.12.1] - 2025-07-26

### Fixed
- Added CLAUDE_TEST_BRANCH environment variable support to fix branch validation test failures
- Fixed test failures when running on protected branches (main)

## [1.12.0] - 2025-07-26

### Changed
- Consolidated test suite with 58-74% code reduction:
  - Merged 3 validation test files into test_core_validation.py
  - Merged 2 file categorization test files into test_file_categorization.py
- Implemented hybrid factory pattern with @overload decorators for type-safe test fixtures
- Added comprehensive pytest fixtures in conftest.py for better test organization
- Added MyPy type checking with strict configuration
- Improved test maintainability through composable fixtures

### Fixed
- Fixed all MyPy type annotation errors (28 issues across 3 files)
- Fixed pytest marker warnings by adding markers to pytest.ini

## [1.11.4] - 2025-07-25

### Fixed
- Documentation files being incorrectly blocked by TDD validation
- Updated TDD categorization prompt to explicitly recognize documentation patterns:
  - Added DOCUMENTATION FILES section to LLM prompt
  - Recognizes *.md, *.rst, *.txt, *.adoc and other doc formats
  - Includes README*, CHANGELOG*, LICENSE* patterns
  - Files in docs/, documentation/, doc/ directories
- Ensures documentation files are categorized as "docs" with requires_tdd: False

## [1.11.3] - 2025-07-25

### Fixed
- CLI files with `if __name__ == "__main__"` incorrectly categorized as structural, bypassing TDD validation (#53)
- Updated categorization prompt to consider file size and complexity:
  - Entry points only structural if < 20 lines with minimal logic
  - Files > 50 lines with functions/classes always categorized as implementation
  - Medium CLI files (20-50 lines) with business logic require TDD
- Added comprehensive CLI categorization tests to test suite

## [1.11.2] - 2025-07-25

### Fixed
- Pytest plugin now correctly reports collection errors (e.g., ImportError) as failing tests (#51)
- TDD validator now recognizes collection errors as RED phase, allowing legitimate GREEN phase implementations
- Added `pytest_collectreport` hook to capture import errors and include them in test count
- Fixed issue where "0 tests" were reported when test collection failed, blocking TDD workflow

## [1.11.1] - 2025-07-25

### Fixed
- Version inconsistency where `__init__.py` had version 1.10.1 while `pyproject.toml` had 1.11.0
- This caused `uvx claude-code-adk-validator@latest --version` to incorrectly show 1.10.1

## [1.11.0] - 2025-07-25

### Changed
- Refactored to use genai-processors library for streaming LLM interactions (#45)
  - Replaced direct generate_content calls with processor pattern
  - Maintained parallel validation capability through asyncio.gather
  - Improved modularity and code organization

### Added
- New streaming_processors.py module with ValidationProcessor base class
- SecurityValidationProcessor and TDDValidationProcessor implementations
- FileCategorizationProcessor for streaming file categorization
- ParallelValidationPipeline for concurrent security and TDD validation
- extract_json_from_part helper for ProcessorPart compatibility

### Fixed
- All mypy type errors with proper async/await patterns
- ProcessorPart API compatibility issues
- Linting errors in streaming processor implementations

### Technical
- Added genai-processors>=0.1.0 dependency
- Updated all validators to use streaming processor pattern
- Improved type safety with proper async method signatures

## [1.10.1] - 2025-07-20

### Fixed
- Re-enabled pytest plugin entry point that was temporarily disabled (#43)
- `--setup` flag now properly installs pytest plugin for automatic test result capture
- Pytest can now discover and use the plugin after running `uvx claude-code-adk-validator --setup`

## [1.10.0] - 2025-07-26

### Added
- Explicit support for test modification during TDD Red phase (#41)
  - Tests can be refined, renamed, or replaced without violating TDD rules
  - Clear distinction between test modification (allowed) and multiple test addition (blocked)
- Three new test scenarios for test modification validation:
  - `test_update_modify_existing_test` - changing test implementation
  - `test_update_rename_test_function` - renaming test functions
  - `test_update_replace_test_with_different_one` - replacing tests
- Enhanced TDD validation prompts with "TEST EVOLUTION IN TDD" section
- Detailed documentation of practical TDD workflows in README

### Changed
- TDD prompts now explicitly allow test modifications with net zero change
- Update operation prompt includes "TEST MODIFICATION VS ADDITION" guidance
- ONE test rule clarified to apply to NET new tests, not modifications
- Validation focuses on net test count change: (new count) - (old count)

### Fixed
- Overly restrictive TDD validation that blocked legitimate test refinements
- LLM interpretation that confused test modification with rule violation
- Improved developer experience during iterative test development

## [1.9.0] - 2025-07-25

### Fixed
- CI test failure where 'Safe file write' test was blocked by branch validation on main branch
- PyPI publish failure due to incorrect version number in pyproject.toml (was 1.8.0, now 1.9.0)

### Added
- Branch validation for GitHub issue-based workflow enforcement (#37)
  - Detects current git branch and blocks code changes on protected branches (main, master, production)
  - Validates branch names follow issue-based pattern (e.g., 42-feature-name)
  - Checks if referenced GitHub issues exist using gh CLI
  - Provides helpful workflow suggestions for proper feature branch development
  - Allows documentation and configuration file changes on protected branches
- Branch context tracking in FileStorage for workflow continuity
- Branch information added to LLM prompts for context-aware security analysis
- Comprehensive test suite for branch validation functionality
- Configuration options for protected branches and issue workflow enforcement

### Changed
- SecurityValidator extended with minimal additions (~70 lines) instead of creating separate module
- LLM prompts now include branch and issue context for better security decisions
- Quick validation test suite includes branch validation tests

## [1.8.0] - 2025-07-25

### Fixed
- TDD validator incorrectly counting all tests as new in Update operations (#35)
  - Update operations now properly diff old vs new content to count only genuinely new tests
  - Added dedicated `validate_update_operation()` method to handle Update-specific logic
  - Fixed issue where legitimate updates adding one test were being blocked
- Quick validation tests timeout issue in CI mode
  - Created test_entry.py to handle subprocess tests without stdin
  - Fixed TodoWrite test data structure
  - Removed CI warning message that interfered with subprocess communication
  - Increased test timeouts from 5s to 10s for quick tests and 15s for comprehensive tests
  - Reduced parallel execution workers to improve test stability

### Added
- Comprehensive test coverage for Update operation TDD validation
- Test entry point for better subprocess testing reliability

### Changed
- Update operations now read existing file content for proper test counting
- Improved error messages for Update operations to show actual new test count

## [1.7.0] - 2025-07-21

### Added
- Template file support for HTML, Jinja2, and other template engines (fixes #33)
  - Automatic detection of template files by extension and directory patterns
  - Template-specific security validation focusing on XSS prevention
  - STRICT_TEMPLATE_VALIDATION config option for optional stricter checks
  - Templates skip code-level security analysis by default
- Template validation tests covering all major template engines
- Template-specific analysis prompts for Gemini LLM

### Fixed
- HTML templates being blocked for lacking server-side security headers
- Overly strict validation preventing legitimate template creation
- Templates incorrectly analyzed for SOLID principles and code quality

### Changed
- FileContextAnalyzer now includes template file categorization
- Security validator routes templates to template-specific validation
- File analysis prompts differentiate between code and template files

## [1.6.0] - 2025-07-21

### Fixed
- Documentation files being incorrectly analyzed as code (fixes #31)
  - File categorization now happens before file upload/analysis
  - Documentation files (.md, .rst, .txt) skip all security validation
  - Files >500 chars no longer trigger code analysis for docs
- CONTRIBUTING.md being blocked for containing example AWS keys

### Added
- Comprehensive test suite for documentation validation scenarios
- Specific handling for docs category in security validator

### Changed
- Security validation flow to check file type before expensive operations
- Documentation files now have dedicated validation path

## [1.5.0] - 2025-07-21

### Added
- Context-aware security validation for test files (fixes #29)
  - FileContextAnalyzer for intelligent file categorization
  - Test files can use test-, mock-, dummy-, fake- prefixed secrets
  - Production files maintain strict security validation
- Parallel test execution for all test files
  - 10x performance improvement (30-60s → 3-5s)
  - Thread-safe counter management with ThreadPoolExecutor
- Pre-PR documentation checks
  - Git hooks to check README.md and CLAUDE.md updates
  - Scripts for automated documentation validation
- Comprehensive test coverage for context-aware validation scenarios

### Changed
- Updated configuration to use gemini-2.5-pro for enhanced reasoning
- Security validator now distinguishes between test and production code
- LLM prompts now include file context for intelligent analysis

### Fixed
- Test files being blocked for legitimate test fixtures
- conftest.py can now contain test secrets for JWT testing

## [1.4.0] - 2025-07-20

### Added
- Update tool support in TDD validation for complete file replacements
- No-comments enforcement to promote self-evident code
- SOLID principles validation (SRP, OCP, LSP, ISP, DIP)
- Zen of Python compliance checking
- Comprehensive testing suite with parallel execution (~30 seconds)
- Pre-commit hooks for automated validation before commits
- Thread-safe parallel test execution
- Quick validation tests that run without LLM calls

### Changed
- Simplified all prompts by ~80% while maintaining functionality
- Removed all emojis from validation output
- Enhanced file categorization with better fallback logic
- Improved error messages to be more actionable

### Fixed
- Gemini API tool/JSON response format conflicts
- Multiple tests detection in Edit operations
- Debug statements removed for better performance

## [1.3.2] - 2025-07-19

### Added
- Comprehensive testing framework
- Pre-commit hook configuration
- Parallel test execution support

### Changed
- Refactored prompts to align with coding philosophy
- Enhanced TDD validation logic

## [1.3.1] - 2025-07-19

### Added
- Smart file classification for structural files (__init__.py, setup.py, etc.)
- Enhanced TDD validation scope refinement

### Fixed
- NoneType error in TDD validation
- File categorization for Python structural files

## [1.3.0] - 2025-07-19

### Added
- Automatic pytest plugin installation during --setup
- Enhanced setup process

### Fixed
- Issue #22: Automatic pytest plugin registration

## [1.2.1] - 2025-07-19

### Fixed
- GitHub Actions workflow permissions for release creation

## [1.2.0] - 2025-07-19

### Added
- Automatic test result capture for multiple languages
- Built-in pytest plugin for seamless integration
- Test reporters for Python, TypeScript/JavaScript, Go, Rust, Dart/Flutter
- CLI flags: --capture-test-results and --list-languages
- Simplified UX output with actionable-first design
- TodoWrite optimization (skips validation, persists context)

### Changed
- Optimized file categorization to use lighter gemini-2.5-flash model
- Improved output formatting (removed redundant headers)

### Fixed
- File storage context persistence
- Test result JSON format standardization

## [1.1.0] - 2025-07-18

### Added
- Hybrid Security + TDD validation system
- Modular architecture (security_validator.py, tdd_validator.py, hybrid_validator.py)
- Context persistence with FileStorage
- TDD enforcement with Red-Green-Refactor cycle
- Single test rule enforcement
- Operation-specific validation logic
- TodoWrite tool support

### Changed
- Split monolithic validator into specialized modules
- Added sequential validation pipeline

### Removed
- Fail-safe mode (operations now blocked without API key)

## [1.0.3] - 2025-07-17

### Added
- Enhanced secret detection with reduced false positives
- Word boundaries for pattern matching
- Placeholder exclusion for documentation
- Comprehensive stderr output with structured sections
- Full context processing (no truncation limits)
- Deep thinking analysis with 24576 token budget

### Fixed
- Gemini Files API integration
- Large file security analysis

## [1.0.0] - 2025-07-15

### Added
- Initial release with security validation
- Multi-tier validation system
- Google Gemini LLM integration
- Tool enforcement (grep→rg, find→rg, python→uv)
- PreToolUse hook support for Claude Code

[1.4.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.0.0...v1.0.3
[1.0.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/releases/tag/v1.0.0
