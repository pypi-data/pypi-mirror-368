# User Guide

This comprehensive guide covers all features and advanced usage patterns of Highlander Enum.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [ExFlag Class](#exflag-class)
3. [OptionsFlag Class](#optionsflag-class)
4. [Conflict Resolution](#conflict-resolution)
5. [Advanced Usage](#advanced-usage)
6. [Type Safety](#type-safety)
7. [Best Practices](#best-practices)

## Core Concepts

### Mutually Exclusive Flags

The fundamental concept behind Highlander Enum is mutual exclusion. When flags are defined as mutually exclusive, only one from the group can be active at any time.

```python
from highlander import ExFlag

class Quality(ExFlag):
    LOW = 1
    MEDIUM = 2
    HIGH = 4
    ULTRA = 8, (LOW, MEDIUM, HIGH)  # ULTRA conflicts with all others
```

### Bitmask Implementation

Under the hood, Highlander Enum uses efficient bitmasks for conflict resolution:

```python
# When you define exclusions, bitmasks are created automatically
class Example(ExFlag):
    A = 1       # Binary: 0001
    B = 2, (A,) # Binary: 0010, excludes A (0001)
    C = 4       # Binary: 0100, no conflicts

# The __exclusives__ mapping stores these relationships
print(Example.__exclusives__)  # Shows the internal bitmasks
```

### Conflict Detection

Conflicts are detected during bitwise operations (`|`, `&`, `^`) and flag creation:

```python
class Mode(ExFlag):
    FAST = 1
    SLOW = 2, (FAST,)

# Conflict detected and resolved during OR operation
result = Mode.FAST | Mode.SLOW  # SLOW wins (RHS default)

# Conflict detected and resolved during flag creation
combined = Mode(3)  # 3 = FAST(1) + SLOW(2), resolves to FAST
```

## ExFlag Class

### Basic Definition

```python
from highlander import ExFlag

class MyFlag(ExFlag):
    # Simple flags (no conflicts)
    FEATURE_A = 1
    FEATURE_B = 2

    # Flag with exclusions
    EXCLUSIVE = 4
MyFlag.EXCLUSIVE.add_exclusions(MyFlag.FEATURE_A, MyFlag.FEATURE_B)
```

### Conflict Resolution Strategies

#### RHS (Right-Hand Side) - Default

```python
class RHSFlag(ExFlag):  # Default behavior
    A = 1
    B = 2, (A,)

result = RHSFlag.A | RHSFlag.B  # B wins
print(result)  # RHSFlag.B
```

#### LHS (Left-Hand Side)

```python
from highlander import LHS

class LHSFlag(ExFlag, conflict=LHS):
    A = 1
    B = 2, (A,)

result = LHSFlag.A | LHSFlag.B  # A wins
print(result)  # LHSFlag.A
```

#### STRICT Mode

```python
from highlander import STRICT

class StrictFlag(ExFlag, conflict=STRICT):
    A = 1
    B = 2, (A,)

try:
    result = StrictFlag.A | StrictFlag.B
except ValueError as e:
    print(f"Error: {e}")  # Error: StrictFlag.B conflicts with StrictFlag.A
```

### Bitwise Operations

All standard bitwise operations work with conflict resolution:

```python
class OpFlag(ExFlag):
    A = 1
    B = 2, (A,)
    C = 4

# OR operation with conflict resolution
result1 = OpFlag.A | OpFlag.B  # OpFlag.B

# AND operation (no conflict resolution needed)
result2 = OpFlag.A & OpFlag.C  # OpFlag(0) if no common bits

# XOR operation with conflict resolution
result3 = OpFlag.A ^ OpFlag.B  # OpFlag.B

# Reverse operations also work
result4 = 1 | OpFlag.B  # OpFlag.B
```

### Dynamic Exclusions

Add exclusions at runtime using the `add_exclusions` method:

```python
class DynamicFlag(ExFlag):
    X = 1
    Y = 2
    Z = 4

# Add exclusions after class creation
flag_x = DynamicFlag.X
flag_x.add_exclusions(DynamicFlag.Y, DynamicFlag.Z)

# Now X conflicts with Y and Z
result = DynamicFlag.X | DynamicFlag.Y
print(result)  # DynamicFlag.X (conflicts resolved)
```

### Class-Level Exclusions

Use `add_mutual_exclusions` to set up complex relationships:

```python
class GroupFlag(ExFlag):
    A = 1
    B = 2
    C = 4
    D = 8

# Make A, B, C mutually exclusive (D remains independent)
GroupFlag.add_mutual_exclusions([GroupFlag.A, GroupFlag.B, GroupFlag.C])

result = GroupFlag.A | GroupFlag.B | GroupFlag.D
print(result)  # GroupFlag.B|D (B wins over A, D is independent)
```

## OptionsFlag Class

`OptionsFlag` extends `ExFlag` with features specifically designed for command-line options and configuration systems.

### Tuple Formats

`OptionsFlag` supports multiple tuple formats for maximum flexibility:

```python
from highlander import OptionsFlag

class CLIOptions(OptionsFlag):
    # Format 1: (value, help_string)
    SIMPLE = 1, "Simple option with help text"

    # Format 2: (value, [aliases], help_string)
    WITH_ALIASES = 2, ["a", "alias"], "Option with aliases"

    # Format 3: (value, [aliases], help_string, [exclusions])
    FULL = 4, ["f", "full"], "Full specification", (WITH_ALIASES,)

    # Format 4: (value, help_string, [exclusions])
    HELP_EXCL = 8, "Help with exclusions", (SIMPLE,)

    # Format 5: (value, [], help_string) - empty aliases
    EMPTY_ALIASES = 16, [], "Option with empty aliases list"
```

### Accessing Metadata

```python
class ServerOpts(OptionsFlag):
    VERBOSE = 1, ["v", "verbose"], "Enable verbose output"
    QUIET = 2, ["q", "quiet"], "Suppress output", (VERBOSE,)
    DEBUG = 4, ["d", "debug"], "Enable debug mode"

# Access help text
print(ServerOpts.VERBOSE.help)    # "Enable verbose output"
print(ServerOpts.QUIET.help)      # "Suppress output"

# Access aliases
print(ServerOpts.VERBOSE.aliases) # ['v', 'verbose']
print(ServerOpts.DEBUG.aliases)   # []

# Aliases are automatically registered for lookups
verbose_flag = ServerOpts._value2member_map_['verbose']
print(verbose_flag == ServerOpts.VERBOSE)  # True
```

### Building CLI Parsers

`OptionsFlag` is perfect for building command-line parsers:

```python
import argparse
from highlander import OptionsFlag

class ProcessorOptions(OptionsFlag):
    FAST = 1, ["f", "fast"], "Fast processing mode"
    ACCURATE = 2, ["a", "accurate"], "Accurate processing mode", (FAST,)
    VERBOSE = 4, ["v", "verbose"], "Verbose output"
    QUIET = 8, ["q", "quiet"], "Quiet mode", (VERBOSE,)

def create_parser():
    parser = argparse.ArgumentParser()

    # Add options based on flag definitions
    for option in ProcessorOptions:
        primary_name = f"--{option.name.lower().replace('_', '-')}"
        aliases = [f"--{alias}" for alias in option.aliases]

        parser.add_argument(
            primary_name, *aliases,
            action='store_true',
            help=option.help
        )

    return parser

# Usage
parser = create_parser()
args = parser.parse_args(['--fast', '--verbose'])

# Convert args to flags
flags = ProcessorOptions(0)
if args.fast: flags |= ProcessorOptions.FAST
if args.accurate: flags |= ProcessorOptions.ACCURATE
if args.verbose: flags |= ProcessorOptions.VERBOSE
if args.quiet: flags |= ProcessorOptions.QUIET

print(flags)  # ProcessorOptions.FAST|VERBOSE
```

## Conflict Resolution

### Understanding Resolution Strategies

Each strategy handles conflicts differently when mutually exclusive flags are combined:

#### RHS Strategy - Practical Example

```python
from highlander import ExFlag

class LogLevel(ExFlag):  # Default: RHS
    ERROR = 1
    WARN = 2
    INFO = 4
    DEBUG = 8, (ERROR, WARN, INFO)

# Building up configuration step by step
config = LogLevel.ERROR
print(f"Initial: {config}")        # Initial: LogLevel.ERROR

config |= LogLevel.WARN
print(f"After WARN: {config}")     # After WARN: LogLevel.WARN (WARN wins)

config |= LogLevel.DEBUG
print(f"After DEBUG: {config}")    # After DEBUG: LogLevel.DEBUG (DEBUG wins)
```

#### LHS Strategy - Preserving Original Values

```python
from highlander import ExFlag, LHS

class SecureMode(ExFlag, conflict=LHS):
    BASIC = 1
    ENHANCED = 2
    MAXIMUM = 4, (BASIC, ENHANCED)

# Once set, original value is preserved
security = SecureMode.MAXIMUM
print(f"Initial: {security}")      # Initial: SecureMode.MAXIMUM

security |= SecureMode.BASIC
print(f"After BASIC: {security}")  # After BASIC: SecureMode.MAXIMUM (preserved)

security |= SecureMode.ENHANCED
print(f"After ENHANCED: {security}")  # After ENHANCED: SecureMode.MAXIMUM (preserved)
```

#### STRICT Strategy - Fail-Fast Validation

```python
from highlander import ExFlag, STRICT

class ValidatedFlag(ExFlag, conflict=STRICT):
    OPTION_A = 1
    OPTION_B = 2, (OPTION_A,)
    OPTION_C = 4

def safe_combine(flag1, flag2):
    try:
        return flag1 | flag2
    except ValueError as e:
        print(f"Cannot combine {flag1} and {flag2}: {e}")
        return None

result1 = safe_combine(ValidatedFlag.OPTION_A, ValidatedFlag.OPTION_C)
print(result1)  # ValidatedFlag.OPTION_A|OPTION_C (no conflict)

result2 = safe_combine(ValidatedFlag.OPTION_A, ValidatedFlag.OPTION_B)
print(result2)  # None (conflict detected and handled)
```

### Conflict Resolution in Complex Scenarios

```python
from highlander import ExFlag

class ComplexFlag(ExFlag):
    # Group 1: Colors
    RED = 1
    GREEN = 2
    BLUE = 4, (RED, GREEN)

    # Group 2: Sizes
    SMALL = 8
    MEDIUM = 16
    LARGE = 32, (SMALL, MEDIUM)

    # Independent
    ANIMATED = 64

# Multiple conflicts resolved simultaneously
complex_value = ComplexFlag.RED | ComplexFlag.GREEN | ComplexFlag.SMALL | ComplexFlag.LARGE | ComplexFlag.ANIMATED

# Results in: GREEN (wins over RED) + LARGE (wins over SMALL) + ANIMATED (no conflict)
print(complex_value)  # ComplexFlag.ANIMATED|GREEN|LARGE
```

## Advanced Usage

### Inheritance and Base Classes

```python
from highlander import ExFlag

class BaseFlag(ExFlag):
    FEATURE_A = 1
    FEATURE_B = 2, (FEATURE_A,)

class ExtendedFlag(BaseFlag):
    FEATURE_C = 4
    FEATURE_D = 8, (FEATURE_B, FEATURE_C)  # Can reference parent flags

# All exclusions work across the inheritance hierarchy
result = ExtendedFlag.FEATURE_A | ExtendedFlag.FEATURE_D
print(result)  # ExtendedFlag.FEATURE_D (wins over FEATURE_A through FEATURE_B)
```

### Auto Values with Exclusions

```python
from enum import auto
from highlander import OptionsFlag

class AutoOptions(OptionsFlag):
    VERBOSE = auto(), ["v"], "Verbose output"
    QUIET = auto(), ["q"], "Quiet mode", (VERBOSE,)
    DEBUG = auto(), ["d"], "Debug mode", (QUIET,)

    # auto() generates power-of-2 values automatically for flags
    FEATURE_X = auto(), "Another feature"

# Check the generated values
for opt in AutoOptions:
    print(f"{opt.name}: {opt.value} (binary: {bin(opt.value)})")
```

### Custom Conflict Handlers

For advanced use cases, you can examine the internal conflict handling:

```python
class CustomFlag(ExFlag):
    A = 1
    B = 2, (A,)
    C = 4

# Examine exclusion masks
print(f"A exclusions: {bin(CustomFlag.__exclusives__[1])}")
print(f"B exclusions: {bin(CustomFlag.__exclusives__[2])}")
print(f"C exclusions: {bin(CustomFlag.__exclusives__[4])}")

# The exclusion mask for A excludes B (value 2)
# So A's mask will be ~2 which allows everything except bit 1
```

### Working with Raw Integers

```python
class IntFlag(ExFlag):
    LOW = 1
    HIGH = 2, (LOW,)
    EXTRA = 4

# Create from raw integers with automatic conflict resolution
flag1 = IntFlag(1 | 2)  # LOW + HIGH conflict
print(flag1)  # IntFlag.LOW (conflict resolved)

flag2 = IntFlag(1 | 4)  # LOW + EXTRA no conflict
print(flag2)  # IntFlag.LOW|EXTRA

# Check membership
if IntFlag.LOW in flag2:
    print("LOW is present")

# Get raw integer value
raw_value = int(flag2)
print(f"Raw value: {raw_value}")  # Raw value: 5
```

## Type Safety

### Type Hints

Highlander Enum provides full type safety:

```python
from typing import Union
from highlander import ExFlag

class TypedFlag(ExFlag):
    OPTION_A = 1
    OPTION_B = 2, (OPTION_A,)

def process_flag(flag: TypedFlag) -> str:
    """Process a flag with full type safety."""
    if flag & TypedFlag.OPTION_A:
        return "Processing A"
    elif flag & TypedFlag.OPTION_B:
        return "Processing B"
    else:
        return "No options"

# Type checkers will validate these calls
result1 = process_flag(TypedFlag.OPTION_A)         # ✓ Valid
result2 = process_flag(TypedFlag.OPTION_A | TypedFlag.OPTION_B)  # ✓ Valid

# This would cause a type error:
# result3 = process_flag("invalid")  # ✗ Type error
```

### Generic Patterns

```python
from typing import TypeVar, Generic
from highlander import ExFlag

T = TypeVar('T', bound=ExFlag)

class ConfigManager(Generic[T]):
    def __init__(self, flag_class: type[T]) -> None:
        self.flag_class = flag_class
        self.current_flags: T = flag_class(0)

    def set_flag(self, flag: T) -> None:
        self.current_flags |= flag

    def get_flags(self) -> T:
        return self.current_flags

# Usage with type safety
class MyFlags(ExFlag):
    A = 1
    B = 2, (A,)

manager = ConfigManager(MyFlags)
manager.set_flag(MyFlags.A)  # Type safe
```

## Best Practices

### 1. Clear Naming Conventions

```python
# Good: Clear, descriptive names
class LoggingMode(ExFlag):
    ERROR_ONLY = 1
    INCLUDE_WARNINGS = 2
    INCLUDE_INFO = 4
    FULL_DEBUG = 8, (ERROR_ONLY, INCLUDE_WARNINGS, INCLUDE_INFO)

# Avoid: Unclear abbreviations
class BadFlag(ExFlag):
    E = 1
    W = 2
    I = 4
    D = 8, (E, W, I)
```

### 2. Logical Grouping

```python
# Good: Group related exclusions logically
class UISettings(ExFlag):
    # Theme group
    LIGHT = 1
    DARK = 2
    HIGH_CONTRAST = 4, (LIGHT, DARK)

    # Size group
    SMALL = 8
    LARGE = 16, (SMALL,)

    # Independent features
    ANIMATIONS = 32
    TOOLTIPS = 64

# Avoid: Mixed unrelated exclusions
class BadSettings(ExFlag):
    LIGHT = 1
    SMALL = 2, (LIGHT,)  # Theme and size shouldn't conflict
    ANIMATIONS = 4, (LIGHT,)  # Animations and theme shouldn't conflict
```

### 3. Document Complex Relationships

```python
class ComplexSystem(ExFlag):
    """System configuration flags with multiple exclusion groups.

    Exclusion Groups:
    - Performance: FAST, BALANCED, THOROUGH
    - Verbosity: QUIET, NORMAL, VERBOSE
    - Output: JSON, XML, CSV
    """

    # Performance group (mutually exclusive)
    FAST = 1
    BALANCED = 2
    THOROUGH = 4, (FAST, BALANCED)

    # Verbosity group (mutually exclusive)
    QUIET = 8
    NORMAL = 16
    VERBOSE = 32, (QUIET, NORMAL)

    # Output format group (mutually exclusive)
    JSON = 64
    XML = 128
    CSV = 256, (JSON, XML)
```

### 4. Use Appropriate Conflict Resolution

```python
# Use RHS for progressive configuration
class ProgressiveConfig(ExFlag):  # Default RHS
    BASIC = 1
    ENHANCED = 2
    PREMIUM = 4, (BASIC, ENHANCED)

# Use LHS for security/stability
class SecurityLevel(ExFlag, conflict=LHS):
    LOW = 1
    MEDIUM = 2
    HIGH = 4, (LOW, MEDIUM)

# Use STRICT for validation
class ValidatedOptions(ExFlag, conflict=STRICT):
    DEVELOPMENT = 1
    PRODUCTION = 2, (DEVELOPMENT,)
```

### 5. Test Edge Cases

```python
import pytest
from highlander import ExFlag

class TestFlag(ExFlag):
    A = 1
    B = 2, (A,)

def test_conflict_resolution():
    """Test that conflicts are resolved correctly."""
    result = TestFlag.A | TestFlag.B
    assert result == TestFlag.B  # RHS wins

def test_integer_creation():
    """Test creating flags from integers."""
    flag = TestFlag(3)  # A + B
    assert flag == TestFlag.A  # Conflict resolved

def test_no_conflict():
    """Test non-conflicting combinations."""
    # Add non-conflicting flag for testing
    class ExtendedFlag(TestFlag):
        C = 4

    result = ExtendedFlag.A | ExtendedFlag.C
    assert result.value == 5  # Should combine normally
```

---

This completes the comprehensive User Guide. For specific implementation examples, see the [Examples](examples.md) section, or check the [API Reference](api-reference.md) for detailed method documentation.
