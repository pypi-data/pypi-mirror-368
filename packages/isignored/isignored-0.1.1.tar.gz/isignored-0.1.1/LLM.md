# isignored

This is a Python package that provides a utility for checking whether a path is ignored by ignore files like `.gitignore`.

## Purpose

The `isignored` package offers a simple API to check if files or directories should be ignored based on patterns in ignore files. It supports:

- Basic gitignore syntax (subset sufficient for most use cases)
- Multiple ignore file types (`.gitignore`, `.dockerignore`, etc.)
- Nested ignore files
- Pattern caching for performance
- Files inside ignored directories are also considered ignored

## Project Structure

```
src/isignored/           # Main package source
  __init__.py           # Contains all implementation and public API
tests/                  # Comprehensive test suite
  test_isignored.py     # All tests for the package
.github/workflows/      # CI/CD
  test.yml             # Run tests on multiple Python versions
  publish.yml          # Publish to PyPI on release
```

## State of the Code Base

- ✅ Complete implementation with comprehensive tests (15 test cases)
- ✅ All tests passing
- ✅ Package builds successfully
- ✅ Ready for PyPI publication
- ✅ CI/CD workflows configured
- ✅ Proper Python packaging structure

## Python Environment

This project uses uv to manage dependencies. The default python points to the local venv. Use `uv add <package>` to install a package.

## Usage

```python
from isignored import is_ignored

# Check if a file is ignored by .gitignore
is_ignored("path/to/file.log")  # True if ignored

# Check against multiple ignore files  
is_ignored("path/to/file", [".gitignore", ".dockerignore"])

# Check with no ignore files
is_ignored("path/to/file", [])  # Always False
```

## Development Commands

- `uv run pytest tests/` - Run tests
- `uv build` - Build package
- `uv run pytest tests/ -v` - Run tests with verbose output

## Release Process

1. Update version in `pyproject.toml`
2. Create a GitHub release
3. The publish workflow will automatically upload to PyPI
