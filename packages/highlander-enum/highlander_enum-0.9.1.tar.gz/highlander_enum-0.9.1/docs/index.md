# 🗡️ Highlander Enum Documentation

[![Release](https://img.shields.io/github/v/release/florean/highlander-enum)](https://img.shields.io/github/v/release/florean/highlander-enum)
[![Build status](https://img.shields.io/github/actions/workflow/status/florean/highlander-enum/main.yml?branch=main)](https://github.com/florean/highlander-enum/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/florean/highlander-enum/branch/main/graph/badge.svg)](https://codecov.io/gh/florean/highlander-enum)
[![Commit activity](https://img.shields.io/github/commit-activity/m/florean/highlander-enum)](https://img.shields.io/github/commit-activity/m/florean/highlander-enum)
[![License](https://img.shields.io/github/license/florean/highlander-enum)](https://img.shields.io/github/license/florean/highlander-enum)

> *"There can be only one!"* - A Python library for mutually exclusive flag enums with smart conflict resolution.

**Highlander Enum** provides `ExFlag` and `OptionsFlag` - specialized variations of Python's `IntFlag` enum designed for scenarios where certain flags must be mutually exclusive. Think command-line options where `--verbose` and `--quiet` can't both be active, or configuration settings where only one mode can be selected at a time.

## ✨ Key Features

- 🚫 **Mutually Exclusive Flags**: Define groups where only one flag can be active
- 🔀 **Smart Conflict Resolution**: Choose how conflicts are handled (RHS wins, LHS wins, or strict mode)
- 🏃 **Performance Optimized**: Uses bitmasks for fast conflict detection during bitwise operations
- 📋 **Command-Line Ready**: `OptionsFlag` includes aliases and help text for CLI tools
- 🎯 **Type Safe**: Full type hints and comprehensive test coverage (100%)
- 🐍 **Modern Python**: Supports Python 3.11, 3.12, and 3.13

## 🚀 Quick Example

```python
from highlander import ExFlag

class NetworkMode(ExFlag):
    # Basic flags that can be combined
    IPV4 = 1
    IPV6 = 2
    ENCRYPTION = 4

    # Mutually exclusive verbosity levels
    QUIET = 16
    VERBOSE = 32
    DEBUG = 64, (QUIET, VERBOSE)  # Can't be combined with QUIET or VERBOSE

# RHS (right-hand side) wins by default
mode = NetworkMode.QUIET | NetworkMode.VERBOSE
print(mode)  # NetworkMode.VERBOSE (VERBOSE wins)

# Non-conflicting flags combine normally
mode = NetworkMode.IPV4 | NetworkMode.ENCRYPTION | NetworkMode.VERBOSE
print(mode)  # NetworkMode.ENCRYPTION|IPV4|VERBOSE
```

## 📚 Documentation Sections

### [Getting Started](getting-started.md)
Learn how to install and get up and running with Highlander Enum in minutes.

### [User Guide](user-guide.md)
Comprehensive guide covering all features, conflict resolution strategies, and advanced usage patterns.

### [Examples](examples.md)
Real-world examples including command-line tools, game configurations, and file processors.

### [API Reference](api-reference.md)
Complete API documentation with detailed method signatures and descriptions.

## 🎯 Use Cases

Highlander Enum is perfect for scenarios where you need mutually exclusive flags:

- **Command-Line Tools**: `--verbose` vs `--quiet` options
- **Configuration Settings**: Quality levels like `LOW`, `MEDIUM`, `HIGH`
- **Game Settings**: Graphics modes, difficulty levels, UI themes
- **Network Protocols**: Connection types, security levels
- **File Processing**: Compression levels, output formats

## 🔧 Core Classes

### `ExFlag`
The main class providing mutually exclusive flag behavior with configurable conflict resolution.

```python
from highlander import ExFlag

class MyFlag(ExFlag, conflict="rhs"):  # RHS, LHS, or STRICT
    A = 1
    B = 2, (A,)  # B conflicts with A
    C = 4
```

### `OptionsFlag`
Specialized for command-line options with aliases and help text.

```python
from highlander import OptionsFlag

class MyOptions(OptionsFlag):
    VERBOSE = 1, ["v", "verbose"], "Enable verbose output"
    QUIET = 2, ["q", "quiet"], "Suppress output", (VERBOSE,)
```

## 🎛️ Conflict Resolution

Choose how conflicts are resolved:

| Strategy | Behavior | Example |
|----------|----------|---------|
| **RHS** (default) | Right-hand side wins | `A \| B` → `B` |
| **LHS** | Left-hand side wins | `A \| B` → `A` |
| **STRICT** | Raises `ValueError` | `A \| B` → Exception |

## 🚀 Installation

```bash
pip install highlander-enum
```

## 🔗 Links

- **Repository**: [https://github.com/florean/highlander-enum](https://github.com/florean/highlander-enum)
- **PyPI**: [https://pypi.org/project/highlander-enum/](https://pypi.org/project/highlander-enum/)
- **Issues**: [Report bugs or request features](https://github.com/florean/highlander-enum/issues)
- **Discussions**: [Community discussions](https://github.com/florean/highlander-enum/discussions)

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/florean/highlander-enum/blob/main/LICENSE) file for details.

---

*"In the end, there can be only one... flag active in each exclusion group!"* 🗡️
