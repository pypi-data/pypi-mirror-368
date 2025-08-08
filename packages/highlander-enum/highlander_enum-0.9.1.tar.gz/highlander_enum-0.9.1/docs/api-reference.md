# API Reference

Complete API documentation for Highlander Enum classes and methods.

## Core Imports

```python
from highlander import ExFlag, OptionsFlag, EnumPlusType, RHS, LHS, STRICT
```

## ExFlag Class

The main class providing mutually exclusive flag behavior with configurable conflict resolution.

### Class Definition

```python
class ExFlag(IntFlag, metaclass=EnumPlusType)
```

**Inherits from:** `enum.IntFlag`
**Metaclass:** `EnumPlusType`

### Class Parameters

When defining an ExFlag subclass, you can specify conflict resolution:

```python
class MyFlag(ExFlag, conflict="rhs"):  # or "lhs", "strict"
    pass
```

**Parameters:**

- `conflict` *(str | ConflictResolution)*: Conflict resolution strategy
  - `"rhs"` or `ConflictResolution.RHS`: Right-hand side wins (default)
  - `"lhs"` or `ConflictResolution.LHS`: Left-hand side wins
  - `"strict"` or `ConflictResolution.STRICT`: Raise ValueError on conflicts

### Class Attributes

#### `__exclusives__`

```python
__exclusives__: ClassVar[defaultdict[int, int]]
```

Class variable storing bitmasks for mutually exclusive flags. Maps flag values to exclusion masks.

**Type:** `defaultdict[int, int]` with default value `-1`

**Example:**
```python
class MyFlag(ExFlag):
    A = 1
    B = 2, [A]

print(MyFlag.__exclusives__[1])  # Exclusion mask for A
print(MyFlag.__exclusives__[2])  # Exclusion mask for B
```

### Instance Creation

#### `__new__(cls, value, *args)`

Create new ExFlag enum members with optional exclusion definitions.

**Parameters:**

- `value` *(int)*: The integer value for this flag
- `*args` *(Any)*: Optional arguments where the last argument can be a list of flags that should be mutually exclusive with this flag

**Returns:** `Self` - A new ExFlag instance

**Example:**
```python
class MyFlag(ExFlag):
    A = 1
    B = 2
    C = 4, [A, B]  # A, B, and C all conflict
```

#### `__call__(cls, value)`

Create an ExFlag instance from an integer value, resolving conflicts.

**Parameters:**

- `value` *(int)*: Integer value to convert to an ExFlag instance

**Returns:** `Self` - An ExFlag instance with conflicts resolved

**Example:**
```python
class MyFlag(ExFlag):
    A = 1
    B = 2, [A]

flag = MyFlag(3)  # 3 = A + B, conflicts resolved
print(flag)  # MyFlag.A (conflict resolved)
```

### Class Methods

#### `add_mutual_exclusions(mutually_exclusive_values)`

```python
@classmethod
def add_mutual_exclusions(cls, mutually_exclusive_values: Sequence[IntFlag | int]) -> None
```

Set multiple flags as mutually exclusive with each other. This is what is used when adding exclusions to a member definition.

**Parameters:**

- `mutually_exclusive_values` *(Sequence[IntFlag | int])*: Sequence of flag values that should be mutually exclusive with each other

**Example:**
```python
class MyFlag(ExFlag):
    A = 1
    B = 2
    C = 4

MyFlag.add_mutual_exclusions([MyFlag.A, MyFlag.B, MyFlag.C])  # Same as C = 4, [A, B]
```

### Instance Methods

#### `add_exclusions(*exclusive_values)`

```python
def add_exclusions(self, *exclusive_values: IntFlag | int) -> None
```

Add flags that are mutually exclusive with this flag instance. This can be used to create more complicated relationships, such as one flag clearing a number of other ones. These should be added right after enum creation, although there are probably some creative ways to use them to dynamically adjust exclusions.

**Parameters:**

- `*exclusive_values` *(IntFlag | int)*: Variable number of flags that should be mutually exclusive with this flag

**Example:**
```python
class MyFlag(ExFlag):
    A = 1
    B = 2
    C = 4

MyFlag.A.add_exclusions(MyFlag.B, MyFlag.C)
MyFlag.B | MyFlag.C == MyFlag.C | MyFlag.B
MyFlag.B | MyFlag.C | MyFlag.A == MyFlag.A
```

### Bitwise Operations

All bitwise operations support conflict resolution:

#### `__or__(self, other)` (|)

Perform bitwise OR operation with conflict resolution.

**Parameters:**

- `other` *(int)*: Integer value to combine with this flag

**Returns:** `Self` - New ExFlag instance with the combined value after conflict resolution

#### `__xor__(self, other)` (^)

Perform bitwise XOR operation with conflict resolution.

**Parameters:**

- `other` *(int)*: Integer value to XOR with this flag

**Returns:** `Self` - New ExFlag instance with the XOR result after conflict resolution

#### `__and__(self, other)` (&)

Standard bitwise AND operation (no conflict resolution required).

**Parameters:**

- `other` *(int)*: Integer value to AND with this flag

**Returns:** `Self` - New ExFlag instance with the AND result

### Reverse Operations

#### `__ror__(self, other)` (other | self)
#### `__rxor__(self, other)` (other ^ self)
#### `__rand__(self, other)` (other & self)

Reverse bitwise operations that delegate to their forward counterparts.

## OptionsFlag Class

Specialized ExFlag subclass for command-line options with aliases and help text.

### Class Definition

```python
class OptionsFlag(ExFlag)
```

**Inherits from:** `ExFlag`

### Instance Creation

#### `__new__(cls, value, *args)`

Create new OptionsFlag members with help text, aliases, and exclusions.

**Parameters:**

- `value` *(int)*: Integer value for this flag
- `*args` *(Any)*: Variable arguments in one of these formats:
  - `(help_str,)` - Just help text
  - `([aliases], help_str)` - Aliases list and help text
  - `([aliases], help_str, (exclusions,))` - Full specification
  - `(help_str, (exclusions,))` - Help text and exclusions

**Returns:** `Self` - New OptionsFlag instance

**Raises:**

- `TypeError`: If no help string is provided or too many arguments are given

**Examples:**
```python
class MyOptions(OptionsFlag):
    # Different tuple formats:
    SIMPLE = 1, "Just help text"
    WITH_ALIASES = 2, ["a", "alias"], "Help with aliases"
    FULL_SPEC = 4, ["f"], "Full spec", (WITH_ALIASES,)
    HELP_EXCLUSIONS = 8, "Help and exclusions", (SIMPLE,)
```

### Properties

#### `help`

```python
@property
def help(self) -> str
```

Get the help text for this flag.

**Returns:** `str` - The help text string provided during flag definition, or empty string if no help text was provided

**Example:**
```python
class MyOptions(OptionsFlag):
    VERBOSE = 1, "Enable verbose output"

print(MyOptions.VERBOSE.help)  # "Enable verbose output"
```

#### `aliases`

```python
@property
def aliases(self) -> list[str]
```

Get the list of aliases for this flag.

**Returns:** `list[str]` - List of string aliases that can be used to reference this flag

**Example:**
```python
class MyOptions(OptionsFlag):
    VERBOSE = 1, ["v", "verbose"], "Enable verbose output"

print(MyOptions.VERBOSE.aliases)  # ['v', 'verbose']
```

## Conflict Resolution Enums

### ConflictResolution

```python
class ConflictResolution(StrEnum)
```

Enumeration defining conflict resolution strategies.

**Values:**

- `RHS`: Right-hand side wins (default)
- `LHS`: Left-hand side wins
- `STRICT`: Raises ValueError on conflicts

**Example:**
```python
from highlander.type import ConflictResolution

class MyFlag(ExFlag, conflict=ConflictResolution.STRICT):
    A = 1
    B = 2, (A,)
```

## Convenience Imports

For convenience, conflict resolution constants are available at package level:

```python
from highlander import LHS, STRICT

# Equivalent to:
from highlander.type import ConflictResolution
LHS = ConflictResolution.LHS
STRICT = ConflictResolution.STRICT
```

## EnumPlusType Metaclass

### Class Definition

```python
class EnumPlusType(EnumType)
```

Metaclass for creating Enum subclasses with support for `super().__new__` for better subclassing, `__call__` to control member lookup, bitwise operation inheritance, control of subclases through `__init_subenum__`, and flexible conflict resolution policies.

**Inherits from:** `enum.EnumType`

### Metaclass Parameters

#### `__new__(metacls, cls, bases, classdict, **kwargs)`

**Parameters:**

- `conflict_enum_cls` *(type[Enum])*: Enum class defining conflict resolution strategies (default: `ConflictResolution`)
- `conflict` *(Enum | str)*: The conflict resolution strategy to use (default: `ConflictResolution.RHS`)
- `boundary` *(Any)*: Boundary handling for flag values (passed to EnumType)
- `_simple` *(bool)*: Whether this is a simple enum (passed to EnumType)
- `**kwds` *(Any)*: Additional keyword arguments passed to parent metaclass

**Returns:** `type` - The newly created enum class

**Raises:**

- `TypeError`: If the conflict resolution strategy is invalid or not implemented

### Static Methods

#### `restore_new_members(bases)`

```python
@staticmethod
def restore_new_members(bases: tuple[type, ...]) -> dict[type, Callable[..., Any] | None]
```

Restore original `__new__` methods from `__new_member__` attributes.

**Parameters:**

- `bases` *(tuple[type, ...])*: Tuple of base classes to examine

**Returns:** `dict[type, Callable[..., Any] | None]` - Dictionary mapping base classes to their original `__new__` methods

#### `restore_news(replaced_new_methods)`

```python
@staticmethod
def restore_news(replaced_new_methods: dict[type, Callable[..., Any] | None]) -> None
```

Restore previously saved `__new__` methods to their original classes.

**Parameters:**

- `replaced_new_methods` *(dict[type, Callable[..., Any] | None])*: Dictionary mapping classes to their original `__new__` methods

## Utility Functions

### `traverse_bases(bases)`

```python
def traverse_bases(bases: tuple[type, ...]) -> tuple[type, ...]
```

Traverse base classes to get an ordered list of the inheritance tree.

**Parameters:**

- `bases` *(tuple[type, ...])*: Tuple of base classes to traverse

**Returns:** `tuple[type, ...]` - Ordered tuple of all classes in the inheritance hierarchy, excluding the built-in object class

### `rebind_method(target_name, target_cls, src_method, src_cls=None)`

```python
def rebind_method(
    target_name: str,
    target_cls: type,
    src_method: classmethod | staticmethod | Callable[..., Any] | str,
    src_cls: type | None = None,
) -> None
```

Rebind a method from one class to another with a new name.

**Parameters:**

- `target_name` *(str)*: The name to give the method in the target class
- `target_cls` *(type)*: The class to which the method should be bound
- `src_method` *(classmethod | staticmethod | Callable[..., Any] | str)*: The source method to copy
- `src_cls` *(type | None)*: The source class containing the method (required if src_method is a string)

**Raises:**

- `ValueError`: If src_method is a string but src_cls is not provided, if the method name is not found in src_cls, or if src_method is not a valid object
- `TypeError`: If src_method is not callable or doesn't have the required function attributes

## Type Annotations

All classes and methods include comprehensive type annotations for full IDE support and type checking with tools like mypy, pyright, and Pylance.

### Common Type Patterns

```python
from typing import Any, ClassVar, Self, Sequence
from enum import IntFlag
from highlander import ExFlag

# Flag instance type
flag: ExFlag = MyFlag.A

# Flag class type
flag_cls: type[ExFlag] = MyFlag

# Sequence of flags for exclusions
exclusions: Sequence[IntFlag | int] = [MyFlag.A, MyFlag.B]

# Exclusions mapping
exclusives: defaultdict[int, int] = MyFlag.__exclusives__
```

## Exception Handling

### ValueError in STRICT Mode

When using STRICT conflict resolution, operations that would cause conflicts raise detailed `ValueError` exceptions:

```python
from highlander import ExFlag, STRICT

class StrictFlag(ExFlag, conflict=STRICT):
    A = 1
    B = 2, (A,)

try:
    result = StrictFlag.A | StrictFlag.B
except ValueError as e:
    print(f"Conflict: {e}")
    # Output: "Conflict: StrictFlag.B conflicts with StrictFlag.A"
```

The error messages provide clear information about which specific flags conflict with each other.

### TypeError in Class Creation

Invalid class definitions or parameters will raise `TypeError`:

```python
# Invalid conflict resolution
try:
    class InvalidFlag(ExFlag, conflict="invalid"):
        A = 1
except TypeError as e:
    print(f"Error: {e}")
    # Output: "Error: Invalid conflict resolution: invalid"

# Missing help text in OptionsFlag
try:
    class InvalidOptions(OptionsFlag):
        NO_HELP = 1  # Missing help text
except TypeError as e:
    print(f"Error: {e}")
    # Output: "Error: A help string is required"
```

---

For practical examples of these APIs in use, see the [Examples](examples.md) section.
