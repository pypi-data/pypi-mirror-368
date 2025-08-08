# Getting Started

Welcome to Highlander Enum! This guide will get you up and running with mutually exclusive flag enums in just a few minutes.

## Installation

Install Highlander Enum using pip:

```bash
pip install highlander-enum
```

### Requirements

- Python 3.11 or higher
- No additional dependencies required

## Your First Highlander Enum

Let's start with a simple example. Imagine you're building a logging system where you want different verbosity levels, but only one can be active at a time:

```python
from highlander import ExFlag

class LogLevel(ExFlag):
    ERROR = 1
    WARN = 2
    INFO = 4
    DEBUG = 8, (ERROR, WARN, INFO)  # Only one logging level can be set

# When flags conflict, the right-hand side (RHS) wins by default
level = LogLevel.ERROR | LogLevel.INFO
print(level)  # LogLevel.INFO (INFO wins over ERROR)

# Non-conflicting flags still work normally
# (In this case, all levels conflict, so you'll always get just one)
```

## Understanding Conflict Resolution

Highlander Enum offers three conflict resolution strategies:

### 1. RHS (Right-Hand Side) - Default

The newest (right-most) value wins when conflicts occur:

```python
from highlander import ExFlag

class Mode(ExFlag):
    FAST = 1
    SLOW = 2, (FAST,)  # SLOW conflicts with FAST

result = Mode.FAST | Mode.SLOW
print(result)  # Mode.SLOW (right side wins)
```

### 2. LHS (Left-Hand Side)

The existing (left-most) value wins when conflicts occur:

```python
from highlander import ExFlag, LHS

class Mode(ExFlag, conflict=LHS):
    FAST = 1
    SLOW = 2, (FAST,)

result = Mode.FAST | Mode.SLOW
print(result)  # Mode.FAST (left side wins)
```

### 3. STRICT Mode

Raises an exception when conflicts occur:

```python
from highlander import ExFlag, STRICT

class Mode(ExFlag, conflict=STRICT):
    FAST = 1
    SLOW = 2, (FAST,)

try:
    result = Mode.FAST | Mode.SLOW
except ValueError as e:
    print(f"Conflict detected: {e}")
    # Output: Conflict detected: Mode.SLOW conflicts with Mode.FAST
```

## Working with Multiple Groups

You can create multiple independent exclusion groups:

```python
from highlander import ExFlag

class UISettings(ExFlag):
    # Color theme group (mutually exclusive)
    LIGHT_THEME = 1
    DARK_THEME = 2
    HIGH_CONTRAST = 4, (LIGHT_THEME, DARK_THEME)

    # Font size group (mutually exclusive)
    SMALL_FONT = 8
    MEDIUM_FONT = 16
    LARGE_FONT = 32, (SMALL_FONT, MEDIUM_FONT)

    # Independent features (no conflicts)
    ANIMATIONS = 64
    SOUND_EFFECTS = 128

# You can mix flags from different groups
settings = UISettings.DARK_THEME | UISettings.LARGE_FONT | UISettings.ANIMATIONS
print(settings)  # UISettings.ANIMATIONS|DARK_THEME|LARGE_FONT

# Conflicts are resolved within groups
settings = UISettings.LIGHT_THEME | UISettings.DARK_THEME | UISettings.SMALL_FONT
print(settings)  # UISettings.DARK_THEME|SMALL_FONT (DARK_THEME wins)
```

## Command-Line Options with OptionsFlag

For command-line tools, use `OptionsFlag` which includes aliases and help text:

```python
from highlander import OptionsFlag

class ServerOptions(OptionsFlag):
    # Format: VALUE, [aliases], "help text", [exclusions]
    VERBOSE = 1, ["v", "verbose"], "Enable verbose logging"
    QUIET = 2, ["q", "quiet"], "Suppress all output", (VERBOSE,)
    DEBUG = 4, ["d", "debug"], "Enable debug mode", (QUIET,)

    # Different tuple formats supported:
    DAEMON = 8, "Run as daemon"  # Just help text
    CONFIG = 16, ["c", "config"], "Specify config file"  # No exclusions

# Access help text and aliases
opt = ServerOptions.VERBOSE
print(f"Help: {opt.help}")      # Help: Enable verbose logging
print(f"Aliases: {opt.aliases}")  # Aliases: ['v', 'verbose']

# Conflicts are resolved automatically
flags = ServerOptions.QUIET | ServerOptions.DEBUG
print(flags)  # ServerOptions.DEBUG (DEBUG wins over QUIET)
```

## Creating Flags from Integer Values

You can create flags from raw integer values, and conflicts will be resolved automatically:

```python
from highlander import ExFlag

class NetworkMode(ExFlag):
    IPV4 = 1
    IPV6 = 2
    QUIET = 4
    VERBOSE = 8, (QUIET,)

# Create from integer with conflicts (1 + 4 + 8 = 13)
# This represents IPV4 + QUIET + VERBOSE, but QUIET and VERBOSE conflict
mode = NetworkMode(13)
print(mode)  # NetworkMode.IPV4|QUIET (conflict resolved, QUIET wins)

# Check if specific flags are set
if NetworkMode.IPV4 in mode:
    print("IPv4 is enabled")  # This will print

if NetworkMode.VERBOSE in mode:
    print("Verbose is enabled")  # This won't print (QUIET won)
```

## Adding Exclusions Dynamically

You can add exclusions at runtime:

```python
from highlander import ExFlag

class DynamicFlag(ExFlag):
    A = 1
    B = 2
    C = 4

# Add exclusions after class creation
flag_a = DynamicFlag.A
flag_a.add_exclusions(DynamicFlag.B, DynamicFlag.C)

# Now A conflicts with B and C
result = DynamicFlag.A | DynamicFlag.B
print(result)  # DynamicFlag.A (conflicts resolved)
```

## Next Steps

Now that you've learned the basics, you can:

1. **[Read the User Guide](user-guide.md)** - Dive deeper into advanced features and patterns
2. **[Check out Examples](examples.md)** - See real-world usage scenarios
3. **[Browse the API Reference](api-reference.md)** - Explore all available methods and options

## Common Patterns

Here are some common patterns you'll use with Highlander Enum:

### Configuration Settings
```python
class Config(ExFlag):
    # Quality levels
    LOW = 1
    MEDIUM = 2
    HIGH = 4
    ULTRA = 8, (OW, MEDIUM, HIGH)

    # Independent features
    COMPRESSION = 16
    ENCRYPTION = 32
```

### State Management (coming soon)
```python
class ConnectionState(ExFlag):
    DISCONNECTED = 1
    CONNECTING = 2, (DISCONNECTED,)
    CONNECTED = 4, (DISCONNECTED, CONNECTING)
    ERROR = 8, (CONNECTING, CONNECTED)
```

### Feature Flags
```python
class Features(OptionsFlag):
    BETA = 1, ["b", "beta"], "Enable beta features"
    EXPERIMENTAL = 2, ["x", "exp"], "Enable experimental features", (BETA,)
    STABLE = 4, ["s", "stable"], "Use only stable features", (BETA, EXPERIMENTAL)
```

That's it! You're now ready to use Highlander Enum in your projects. Remember: *"There can be only one!"* 🗡️
