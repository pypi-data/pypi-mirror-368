# Version Bump Checklist

When bumping the version of cc-validator, ensure all the following locations are updated:

## Required Updates

1. **`pyproject.toml`**
   - Update the `version` field under `[project]`
   ```toml
   [project]
   name = "cc-validator"
   version = "X.Y.Z"  # Update this
   ```

2. **`cc_validator/__init__.py`**
   - Update the `__version__` variable
   ```python
   __version__ = "X.Y.Z"  # Update this
   ```

## Version Format

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

## Pre-Release Checklist

Before bumping version:
1. Run full test suite: `uv run pytest`
2. Check all tests pass (no skipping)
3. Update CHANGELOG.md with release notes
4. Commit all changes

## Post-Release Checklist

After version bump:
1. Create git tag: `git tag vX.Y.Z`
2. Push tag: `git push origin vX.Y.Z`
3. Verify PyPI deployment via GitHub Actions
4. Confirm new version on PyPI

## Plugin Notes

The pytest plugin (`cc_validator.pytest_plugin`) uses the package version and doesn't require separate version updates. It's registered via entry points in `pyproject.toml`.
