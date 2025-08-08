# 🗡️ Highlander Enum

[![Release](https://img.shields.io/github/v/release/florean/highlander-enum)](https://img.shields.io/github/v/release/florean/highlander-enum)
[![Build status](https://img.shields.io/github/actions/workflow/status/florean/highlander-enum/main.yml?branch=main)](https://github.com/florean/highlander-enum/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/florean/highlander-enum/branch/main/graph/badge.svg)](https://codecov.io/gh/florean/highlander-enum)
[![Commit activity](https://img.shields.io/github/commit-activity/m/florean/highlander-enum)](https://img.shields.io/github/commit-activity/m/florean/highlander-enum)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/florean/django-front-runner/blob/main/LICENSE)

> *"There can be only one!"* - A Python library for mutually exclusive flag enums with smart conflict resolution.

**Highlander Enum** provides `ExFlag` and `OptionsFlag` - specialized variations of Python's `IntFlag` enum designed for scenarios where certain flags must be mutually exclusive. Think command-line options where `--verbose` and `--quiet` can't both be active, or configuration settings where only one mode can be selected at a time.

## ✨ Key Features

- 🚫 **Mutually Exclusive Flags**: Define groups where only one flag can be active
- 🔀 **Smart Conflict Resolution**: Choose how conflicts are handled (RHS wins, LHS wins, or strict mode)
- 🏃 **Performance Optimized**: Uses bitmasks for fast conflict detection during bitwise operations
- 📋 **Command-Line Ready**: `OptionsFlag` includes aliases and help text for CLI tools
- 🎯 **Type Safe**: Full type hints and comprehensive test coverage (100%)
- 🐍 **Modern Python**: Supports Python 3.11, 3.12, and 3.13

## 🚀 Quick Start

### Installation

```bash
pip install highlander-enum
```

### Basic Usage

```python
from highlander import ExFlag

class NetworkMode(ExFlag):
    # Basic flags that can be combined
    IPV4 = 1
    IPV6 = 2
    ENCRYPTION = 4
    COMPRESSION = 8

    # Mutually exclusive verbosity levels
    QUIET = 16
    VERBOSE = 32
    DEBUG = 64, (QUIET, VERBOSE)

# RHS (right-hand side) wins by default
mode = NetworkMode.QUIET | NetworkMode.VERBOSE
print(mode)  # NetworkMode.VERBOSE (VERBOSE wins)

# Non-conflicting flags combine normally
mode = NetworkMode.IPV4 | NetworkMode.ENCRYPTION | NetworkMode.VERBOSE
print(mode)  # NetworkMode.ENCRYPTION|IPV4|VERBOSE
```

## 🎛️ Conflict Resolution Strategies

Choose how conflicts should be resolved when mutually exclusive flags are combined:

### RHS (Right-Hand Side) - Default
```python
class LogLevel(ExFlag):  # Default: conflict="rhs"
    ERROR = 1
    WARN = 2
    INFO = 4, (ERROR, WARN)

result = LogLevel.ERROR | LogLevel.INFO
print(result)  # LogLevel.INFO (newer value wins)
```

### LHS (Left-Hand Side)
```python
class LogLevel(ExFlag, conflict="lhs"):
    ERROR = 1
    WARN = 2
    INFO = 4, (ERROR, WARN)

result = LogLevel.ERROR | LogLevel.INFO
print(result)  # LogLevel.ERROR (existing value wins)
```

### Strict Mode
```python
class LogLevel(ExFlag, conflict="strict"):
    ERROR = 1
    WARN = 2
    INFO = 4, (ERROR, WARN)

try:
    result = LogLevel.ERROR | LogLevel.INFO
except ValueError as e:
    print(e)  # LogLevel.INFO conflicts with LogLevel.ERROR
```

## 🖥️ Command-Line Options with OptionsFlag

Perfect for building CLI tools with rich help text and aliases:

```python
from highlander import OptionsFlag

class ServerOptions(OptionsFlag):
    # Format: VALUE, [aliases], "help text", [exclusions]
    VERBOSE = 1, ["v", "verbose"], "Enable verbose logging"
    QUIET = 2, ["q", "quiet"], "Suppress all output"
    DEBUG = 4, ["d", "debug"], "Enable debug mode", (VERBOSE, QUIET)

    # Different tuple formats supported
    DAEMON = 8, "Run as daemon"  # Just help text
    CONFIG = 16, ["c", "config"], "Specify config file"  # No exclusions
    FORCE = 32, "Force operation", (DAEMON,)  # Help + exclusions

# Access help text and aliases
opt = ServerOptions.VERBOSE
print(f"Help: {opt.help}")      # Help: Enable verbose logging
print(f"Aliases: {opt.aliases}")  # Aliases: ['v', 'verbose']

# Smart conflict resolution
flags = ServerOptions.QUIET | ServerOptions.DEBUG
print(flags)  # ServerOptions.DEBUG (DEBUG wins over QUIET)
```

## 🔧 Advanced Usage

### Dynamic Exclusions

Add exclusions at runtime:

```python
class DynamicFlag(ExFlag):
    A = 1
    B = 2
    C = 4

flag_a = DynamicFlag.A
flag_a.add_exclusions(DynamicFlag.B, DynamicFlag.C)

result = DynamicFlag.A | DynamicFlag.B
print(result)  # DynamicFlag.A (conflicts resolved)
```

### Multiple Exclusion Groups

Create complex relationships between different groups of flags:

```python
class UITheme(ExFlag):
    # Color schemes (mutually exclusive)
    DARK = 1
    LIGHT = 2
    HIGH_CONTRAST = 4, (DARK, LIGHT)

    # Size options (separate exclusion group)
    SMALL = 8
    MEDIUM = 16
    LARGE = 32, (SMALL, MEDIUM)

    # Independent options (no conflicts)
    ANIMATIONS = 64
    SOUND_EFFECTS = 128

# Mix and match from different groups
theme = UITheme.DARK | UITheme.LARGE | UITheme.ANIMATIONS
print(theme)  # UITheme.ANIMATIONS|DARK|LARGE

# Conflicts within groups are resolved
theme = UITheme.DARK | UITheme.LIGHT | UITheme.SMALL
print(theme)  # UITheme.LIGHT|SMALL (LIGHT wins over DARK)
```

### Working with Integer Values

```python
# Create flags from integer values with automatic conflict resolution
mixed_flags = NetworkMode(1 | 16 | 32)  # IPV4 + QUIET + VERBOSE
print(mixed_flags)  # NetworkMode.IPV4|QUIET (conflicts resolved)

# Check if flags are set
if NetworkMode.IPV4 in mixed_flags:
    print("IPv4 is enabled")
```

## 🛡️ Type Safety & IDE Support

Highlander Enum provides full type hints for excellent IDE support:

```python
from highlander import ExFlag

class StatusFlag(ExFlag):
    IDLE = 1
    BUSY = 2, (IDLE,)
    ERROR = 4

def process_status(status: StatusFlag) -> str:
    if status & StatusFlag.ERROR:
        return "Error occurred"
    elif status & StatusFlag.BUSY:
        return "Currently busy"
    else:
        return "Ready"

# IDE will provide autocompletion and type checking
result = process_status(StatusFlag.BUSY | StatusFlag.ERROR)
print(result)  # "Error occurred"
```

## 📊 Performance

Highlander Enum is designed for performance with bitwise operations:

```python
import timeit
from highlander import ExFlag

class PerfTest(ExFlag):
    A = 1
    B = 2, (A,)
    C = 4
    D = 8

# Fast bitwise operations with conflict resolution
def test_operations():
    return PerfTest.A | PerfTest.B | PerfTest.C

# Benchmark shows minimal overhead compared to standard IntFlag
print(f"Time per operation: {timeit.timeit(test_operations, number=100000):.6f}s")
```

## 🧪 Real-World Examples

### File Processing Tool

```python
from highlander import OptionsFlag

class FileProcessor(OptionsFlag):
    # Output verbosity (mutually exclusive)
    SILENT = 1, ["s", "silent"], "No output"
    NORMAL = 2, ["n", "normal"], "Normal output"
    VERBOSE = 4, ["v", "verbose"], "Verbose output", (SILENT, NORMAL)

    # Processing modes (mutually exclusive)
    FAST = 8, ["f", "fast"], "Fast processing"
    ACCURATE = 16, ["a", "accurate"], "Accurate processing", (FAST,)

    # Independent options
    BACKUP = 32, ["b", "backup"], "Create backups"
    COMPRESS = 64, ["c", "compress"], "Compress output"

def process_files(options: FileProcessor):
    if options & FileProcessor.VERBOSE:
        print("Verbose mode enabled")
    if options & FileProcessor.BACKUP:
        print("Creating backups")

# Usage
opts = FileProcessor.VERBOSE | FileProcessor.ACCURATE | FileProcessor.BACKUP
process_files(opts)
```

### Game Settings

```python
from highlander import ExFlag

class GraphicsSettings(ExFlag):
    # Quality levels (mutually exclusive)
    LOW = 1
    MEDIUM = 2
    HIGH = 4
    ULTRA = 8, (LOW, MEDIUM, HIGH)

    # Independent features
    VSYNC = 16
    HDR = 32
    ANTIALIASING = 64

class GameConfig:
    def __init__(self):
        self.graphics = GraphicsSettings.MEDIUM | GraphicsSettings.VSYNC

    def upgrade_quality(self):
        # Automatically resolves conflicts
        self.graphics |= GraphicsSettings.HIGH

    def toggle_hdr(self):
        self.graphics ^= GraphicsSettings.HDR

config = GameConfig()
print(config.graphics)  # GraphicsSettings.VSYNC|MEDIUM

config.upgrade_quality()
print(config.graphics)  # GraphicsSettings.VSYNC|HIGH (conflict resolved)
```

## 🏗️ Development

### Requirements

- Python 3.11+
- uv (recommended) or pip

### Setup

```bash
git clone https://github.com/florean/highlander-enum.git
cd highlander-enum
make install  # Sets up virtual environment and pre-commit hooks
```

### Testing

```bash
make test          # Run pytest with coverage
make check         # Run all quality checks (linting, type checking, etc.)
tox               # Test across multiple Python versions
```

### Building Documentation

```bash
make docs         # Serve documentation locally
make docs-test    # Test documentation build
```

## 📈 Project Roadmap

### For 1.0
- New conflict resolutions: smallest wins and largest wins
- More robust constraint specification at member definition
- Better CLI integration for OptionsFlag - more helper methods or parser-specific subclasses
- Solidify internal API and naming
- More real-world usage

### Future Enhancements
- Allow inheriting from and extending existing enums

## 🤝 Contributing

Contributions are welcome! This project maintains **100% test coverage** because reliability is paramount. Please:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests for new functionality (we can help!)
4. Ensure all tests pass and coverage remains 100%
5. Submit a pull request

For bug reports, please open an [issue](https://github.com/florean/highlander-enum/issues).
For feature requests or discussions about potential enhancements, start a [discussion](https://github.com/florean/highlander-enum/discussions).

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://florean.github.io/highlander-enum/](https://florean.github.io/highlander-enum/)
- **Repository**: [https://github.com/florean/highlander-enum](https://github.com/florean/highlander-enum)
- **PyPI**: [https://pypi.org/project/highlander-enum/](https://pypi.org/project/highlander-enum/)

---

*"In the end, there can be only one... flag active in each subset of flags, unless you use add_exclusions and only apply it to one side, in which case yo—🗡️"*
