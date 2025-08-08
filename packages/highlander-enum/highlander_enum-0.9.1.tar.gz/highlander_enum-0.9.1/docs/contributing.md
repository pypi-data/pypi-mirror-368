# Contributing to Highlander Enum

Thank you for your interest in contributing to Highlander Enum! This project maintains **100% test coverage** because reliability is paramount for a library that works at such a fundamental level.

## 🚀 Quick Start for Contributors

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setting Up the Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/highlander-enum.git
   cd highlander-enum
   ```

2. **Set up the development environment:**
   ```bash
   make install  # Sets up virtual environment and pre-commit hooks
   ```

   Or manually with uv:
   ```bash
   uv sync
   uv run pre-commit install
   ```

3. **Verify your setup:**
   ```bash
   make check  # Run all quality checks
   make test   # Run tests with coverage
   ```

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests for a specific file
uv run python -m pytest tests/test_exflag.py -v

# Run a specific test
uv run python -m pytest tests/test_exflag.py::test_mutually_exclusive_flag_creation -v

# Run tests across multiple Python versions
tox
```

### Code Quality Checks

```bash
# Run all quality checks (linting, type checking, dependency checking)
make check

# Individual checks
uv run pre-commit run -a    # Linting and formatting
uv run ty check             # Type checking
uv run deptry .             # Check for obsolete dependencies
```

### Building Documentation

```bash
# Serve documentation locally
make docs

# Test documentation build
make docs-test
```

### Building the Package

```bash
# Build wheel file
make build
```

## 📝 Code Style and Standards

### Code Formatting

We use `ruff` for both linting and formatting:

- Line length: 100 characters
- Follow PEP 8 with project-specific rules in `pyproject.toml`
- Pre-commit hooks automatically format code

### Type Hints

- **All new code must include comprehensive type hints**
- Use modern Python typing features (Python 3.11+)
- Import types from `typing` for compatibility

```python
from typing import Any, ClassVar, Self, Sequence
from collections.abc import Callable

def my_function(value: int, flags: Sequence[ExFlag]) -> Self:
    """Example of proper type hints."""
    pass
```

### Docstrings

We use **Google-style docstrings** for all public APIs:

```python
def add_exclusions(self, *exclusive_values: IntFlag | int) -> None:
    """Add flags that are mutually exclusive with this flag instance.

    This method allows runtime addition of exclusion relationships between
    this flag and other flags. It creates bidirectional exclusions.

    Args:
        *exclusive_values: Variable number of flags (integers or IntFlag
            instances) that should be mutually exclusive with this flag.

    Example:
        >>> flag_a = MyFlag.A
        >>> flag_a.add_exclusions(MyFlag.B, MyFlag.C)
    """
```

### Testing Requirements

- **100% test coverage is mandatory**
- Write tests for all new functionality
- Include edge cases and error conditions
- Test all conflict resolution strategies
- Use descriptive test names

```python
def test_strict_conflict_resolution_with_multiple_groups():
    """Test that STRICT mode properly detects conflicts across multiple exclusion groups."""
    # Test implementation here
```

## 🔧 Types of Contributions

### 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the problem
2. **Minimal reproduction case**
3. **Expected vs actual behavior**
4. **Python version and platform**
5. **Highlander Enum version**

**Template:**
```markdown
**Description**
Brief description of the bug.

**Reproduction**
```python
from highlander import ExFlag

class TestFlag(ExFlag):
    A = 1
    B = 2, [A]

# This should work but doesn't
result = TestFlag.A | TestFlag.B
```

**Expected:** `TestFlag.B`
**Actual:** `TestFlag.A`

**Environment:**
- Python: 3.13.5
- Platform: macOS 14.1
- Highlander Enum: 0.9.1
```

### 💡 Feature Requests

For new features, please:

1. **Search existing discussions** to avoid duplicates
2. **Describe the use case** that motivates the feature
3. **Provide examples** of how it would be used
4. **Consider backwards compatibility**

### 🔨 Code Contributions

#### Small Changes

For small changes (bug fixes, documentation improvements):

1. Fork the repository
2. Create a feature branch: `git checkout -b fix-issue-123`
3. Make your changes
4. Add tests if applicable
5. Run quality checks: `make check`
6. Commit with descriptive message
7. Push and create a pull request

#### Large Changes

For significant changes (new features, architectural changes):

1. **Open a discussion first** to discuss the approach
2. Get maintainer approval before starting work
3. Consider breaking the work into smaller PRs
4. Update documentation as needed

#### Pull Request Process

1. **Ensure all tests pass** and coverage remains 100%
2. **Update documentation** for any API changes
3. **Add changelog entry** if needed
4. **Use descriptive commit messages**

**Commit Message Format:**
```
type(scope): short description

Longer explanation if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

## 📊 Testing Guidelines

### Test Organization

```
tests/
├── test_exflag.py          # Tests for ExFlag class
├── test_optionsflag.py     # Tests for OptionsFlag class
├── test_enumplustype.py    # Tests for EnumPlusType metaclass
└── conftest.py             # Pytest configuration (if needed)
```

### Test Patterns

#### Testing Conflict Resolution

```python
def test_rhs_conflict_resolution():
    """Test RHS conflict resolution strategy."""
    class TestFlag(ExFlag):  # Default RHS
        A = 1
        B = 2, [A]

    result = TestFlag.A | TestFlag.B
    assert result == TestFlag.B  # RHS wins

def test_lhs_conflict_resolution():
    """Test LHS conflict resolution strategy."""
    class TestFlag(ExFlag, conflict=LHS):
        A = 1
        B = 2, [A]

    result = TestFlag.A | TestFlag.B
    assert result == TestFlag.A  # LHS wins

def test_strict_conflict_resolution():
    """Test STRICT conflict resolution raises ValueError."""
    class TestFlag(ExFlag, conflict=STRICT):
        A = 1
        B = 2, [A]

    with pytest.raises(ValueError, match="conflicts with"):
        TestFlag.A | TestFlag.B
```

#### Testing Edge Cases

```python
def test_empty_exclusions():
    """Test flags with empty exclusion lists combine normally."""
    class TestFlag(ExFlag):
        A = 1, []  # Empty exclusions
        B = 2

    result = TestFlag.A | TestFlag.B
    assert result.value == 3  # Should combine normally

def test_self_exclusion_error():
    """Test that flags cannot exclude themselves."""
    with pytest.raises(ValueError):
        class InvalidFlag(ExFlag):
            A = 1, [A]  # This should be invalid
```

#### Testing OptionsFlag

```python
def test_options_flag_help_text():
    """Test that help text is properly stored and accessible."""
    class TestOptions(OptionsFlag):
        VERBOSE = 1, "Enable verbose output"

    assert TestOptions.VERBOSE.help == "Enable verbose output"

def test_options_flag_aliases():
    """Test that aliases are properly registered."""
    class TestOptions(OptionsFlag):
        VERBOSE = 1, ["v", "verbose"], "Enable verbose output"

    assert "v" in TestOptions.VERBOSE.aliases
    assert "verbose" in TestOptions.VERBOSE.aliases
    assert TestOptions._value2member_map_["v"] == TestOptions.VERBOSE
```

### Coverage Requirements

- **Line coverage: 100%**
- **Branch coverage: 100%**
- **All public methods must be tested**
- **All error conditions must be tested**

Check coverage with:
```bash
make test  # Includes coverage report
```

## 📚 Documentation Guidelines

### API Documentation

- All public APIs must have comprehensive docstrings
- Include examples in docstrings when helpful
- Document parameters, return values, and exceptions
- Use type hints consistently

### User Documentation

When adding features that affect users:

1. **Update the User Guide** with new patterns
2. **Add examples** to the Examples section
3. **Update API Reference** if needed
4. **Add to Getting Started** for basic features

### Documentation Testing

Test that examples in documentation work:

```bash
make docs-test
```

## 🚦 Release Process

Maintainers handle releases, but contributors should:

1. **Update version numbers** if instructed
2. **Add changelog entries** for significant changes
3. **Ensure documentation is current**

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn the codebase
- Celebrate contributions from all skill levels

### Communication

- **GitHub Issues**: Bug reports
- **GitHub Discussions**: Feature requests, Questions, ideas, general discussion
- **Pull Request Reviews**: Code feedback and suggestions

## 🔍 Debugging Tips

### Common Development Issues

**Tests failing locally but not in CI:**
```bash
# Ensure you have the same Python version as CI
python --version

# Run tests with the same settings as CI
uv run python -m pytest tests/ -v
```

**Type checking errors:**
```bash
# Run type checker locally
uv run ty check

# Check specific file
uv run ty check highlander/enums.py
```

**Coverage not 100%:**
```bash
# Run coverage with branch analysis
uv run python -m pytest --cov=highlander --cov-branch --cov-report=html tests/

# Open coverage report
open htmlcov/index.html
```

### Debugging Conflict Resolution

```python
# Check exclusion masks
class DebugFlag(ExFlag):
    A = 1
    B = 2, [A]

print(f"A exclusions: {bin(DebugFlag.__exclusives__[1])}")
print(f"B exclusions: {bin(DebugFlag.__exclusives__[2])}")

# Test conflict resolution step by step
flag_a = DebugFlag.A
mask = flag_a._handle_conflict(DebugFlag.B)
print(f"Conflict mask: {bin(mask)}")
```

## 🎯 Good First Issues

New contributors might want to start with:

- Documentation improvements
- Additional test cases
- Type hint improvements
- Example code additions

Look for issues labeled `good-first-issue` or `help-wanted`.

## ❓ Getting Help

If you need help:

1. **Check existing documentation** and examples
2. **Search closed issues** for similar problems
3. **Ask in GitHub Discussions** for general questions or feature requests
4. **Open an issue** for specific bugs

## 🙏 Recognition

All contributors are recognized in:

- Git commit history
- GitHub contributors page
- Release notes (for significant contributions)

Thank you for helping make Highlander Enum better! 🗡️

---

*"In the end, there can be only one... way to do things right: with tests!"* 🧪
