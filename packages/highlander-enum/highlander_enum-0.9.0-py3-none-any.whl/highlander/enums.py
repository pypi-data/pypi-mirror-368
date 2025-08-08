from collections import defaultdict
from collections.abc import Sequence
from enum import Enum, IntFlag
from functools import reduce
from typing import Any, ClassVar, Self

from .type import EnumPlusType


class ExFlag(IntFlag, metaclass=EnumPlusType):
    """An IntFlag variation supporting mutually exclusive flags with configurable conflict resolution.

    ExFlag extends Python's IntFlag to provide "Highlander" behavior - when mutually
    exclusive flags are combined, only one can remain active (there can be only one).
    The conflict resolution strategy determines which flag wins when conflicts occur.

    Flags can define mutual exclusions by passing a list of conflicting flags during
    definition. When conflicting flags are combined using bitwise operations, the
    configured conflict resolution strategy determines the outcome.

    Attributes:
        __exclusives__: Class variable storing bitmasks for mutually exclusive flags.

    Examples:
        Basic usage with RHS (default) conflict resolution:
            >>> class MyFlag(ExFlag):
            ...     FLAG1 = 1
            ...     FLAG2 = 2
            ...     EXCLUSIVE = 4, [FLAG1, FLAG2]  # Conflicts with FLAG1 and FLAG2
            >>> result = MyFlag.FLAG1 | MyFlag.EXCLUSIVE
            >>> result == MyFlag.EXCLUSIVE  # RHS wins
            True

        Using different conflict resolution strategies:
            >>> class StrictFlag(ExFlag, conflict="strict"):
            ...     A = 1
            ...     B = 2, [A]
            >>> StrictFlag.A | StrictFlag.B  # Raises ValueError
            Traceback (most recent call last):
            ValueError: ...conflicts with...
    """

    __exclusives__: ClassVar[defaultdict[int, int]] = defaultdict(lambda: -1)

    def __init_subenum__(classdict: dict[str, Any], **kwargs: Any) -> None:
        """Initialize exclusives tracking for each subclass.

        This method is called by the metaclass to ensure each ExFlag subclass
        gets its own exclusives dictionary, preventing contamination between
        different enum classes.

        Args:
            classdict: Dictionary of class attributes being created.
            **kwargs: Additional keyword arguments (unused).

        Note:
            This is required because __init_subclass__ isn't called until after
            all enum members and __new__ have been processed.
        """
        classdict["__exclusives__"] = defaultdict(lambda: -1)

    def __new__(cls: type["ExFlag"], value: int, *args: Any) -> Self:
        """Create new ExFlag enum members with optional exclusion definitions.

        Args:
            cls: The ExFlag class being instantiated.
            value: The integer value for this flag.
            *args: Optional arguments where the last argument can be a list
                of flags that should be mutually exclusive with this flag.

        Returns:
            A new ExFlag instance with the specified value and exclusions.

        Note:
            If exclusions are provided, they are automatically registered
            as mutually exclusive with this flag using add_mutual_exclusions.
        """
        self = int.__new__(cls, value)
        self._value_ = value
        if not args:
            return self
        ex_flags: list[int] = [x if isinstance(x, int) else x[0] for x in args[-1]]
        ex_flags.append(value)
        cls.add_mutual_exclusions(ex_flags)
        return self

    def __call__(cls: type["ExFlag"], value: int | Any) -> Self:
        """Create an ExFlag instance from an integer value, resolving conflicts.

        This method is called when creating enum instances from integer values,
        such as MyFlag(5). It applies conflict resolution by examining each bit
        in the value and removing conflicting flags according to the exclusion masks.

        Args:
            cls: The ExFlag class.
            value: Integer value to convert to an ExFlag instance.

        Returns:
            An ExFlag instance with conflicts resolved according to the
            class's conflict resolution strategy.

        Note:
            For STRICT mode, _handle_conflict may raise a ValueError if
            conflicts are detected in the original value.
        """
        if not isinstance(value, int):
            if value in cls._member_map_:
                return cls[value]
            else:
                raise ValueError(f"{value} is not a valid {cls.__name__}")  # noqa: TRY003
            return Enum.__new__(cls, value)
        cleaned_value = value
        for x in range(cleaned_value.bit_length()):
            if set_bit := 1 << x & cleaned_value:
                cleaned_value &= cls.__exclusives__[set_bit]
        new: Self = Enum.__new__(cls, cleaned_value)
        new._handle_conflict(value)  # Basically just so STRICT can throw an error
        return new

    @classmethod
    def add_mutual_exclusions(cls, mutually_exclusive_values: Sequence[IntFlag | int]) -> None:
        """Set multiple flags as mutually exclusive with each other.

        Creates bitmasks stored in the __exclusives__ mapping for fast conflict
        resolution during bitwise operations. All flags in the sequence will be
        mutually exclusive with each other - only one from the group can be
        active at a time.

        Args:
            mutually_exclusive_values: Sequence of flag values (integers or IntFlag
                instances) that should be mutually exclusive with each other.

        Example:
            >>> class MyFlag(ExFlag):
            ...     A = 1
            ...     B = 2
            ...     C = 4
            >>> MyFlag.add_mutual_exclusions([MyFlag.A, MyFlag.B, MyFlag.C])
            >>> result = MyFlag.A | MyFlag.B  # B wins (RHS)
            >>> result == MyFlag.B
            True
        """
        ex_values: list[int] = [
            x.value if hasattr(x, "value") else x
            for x in mutually_exclusive_values  # pyright: ignore[reportAttributeAccessIssue]
        ]  # pyright: ignore[reportAttributeAccessIssue]
        # Create the combined mask of all exclusive values
        mask = reduce(lambda x, y: x | y, ex_values)

        # For each value, create an exclusion mask that removes all other values in the group
        for value in ex_values:
            # The exclusion mask allows this value but excludes all others in the group
            cls.__exclusives__[value] = ~(mask & ~value)

    def add_exclusions(self, *exclusive_values: IntFlag | int) -> None:
        """Add flags that are mutually exclusive with this flag instance.

        This method allows runtime addition of exclusion relationships between
        this flag and other flags. It creates bidirectional exclusions - this
        flag will exclude the specified flags, and the specified flags will
        exclude this flag.

        Args:
            *exclusive_values: Variable number of flags (integers or IntFlag
                instances) that should be mutually exclusive with this flag.

        Example:
            >>> class MyFlag(ExFlag):
            ...     A = 1
            ...     B = 2
            ...     C = 4
            >>> flag_a = MyFlag.A
            >>> flag_a.add_exclusions(MyFlag.B, MyFlag.C)
            >>> result = MyFlag.A | MyFlag.B  # B wins due to RHS resolution
            >>> result == MyFlag.B
            True
        """
        values: list[int] = [x.value if hasattr(x, "value") else x for x in exclusive_values]
        combined_mask: int = reduce(lambda x, y: x | y, values)

        # This flag excludes the specified values
        self.__class__.__exclusives__[self.value] &= ~combined_mask

        # The specified values exclude this flag
        for value in values:
            self.__class__.__exclusives__[value] &= ~self.value

    def _handle_conflict(
        self, other: int
    ) -> int:  # pragma: no cover - this gets overwritten with the correct method
        """Base conflict handling method that gets replaced by the metaclass.

        This method is dynamically replaced with the appropriate conflict handler
        (__handle_conflict_rhs__, __handle_conflict_lhs__, or __handle_conflict_strict__)
        based on the conflict resolution strategy specified during class creation.

        Args:
            other: Integer value representing the conflicting flag(s).

        Returns:
            Integer bitmask for resolving conflicts, or -1 as a fallback.

        Note:
            This method should never be called directly in normal usage as it's
            replaced by the metaclass during class creation.
        """
        return -1

    def __handle_conflict_rhs__(self, other: int) -> int:
        """Handle conflicts using RHS (right-hand side) resolution strategy.

        In RHS mode, when conflicting flags are combined, the right-hand side
        (newer) value wins. This is the default conflict resolution strategy.

        Args:
            other: Integer value containing the new flag(s) being combined.

        Returns:
            Bitmask that removes conflicting bits, allowing the RHS value to win.

        Example:
            If flag A conflicts with flag B, then A | B results in B.
        """
        mask: int = -1
        other = int(other)
        for x in range(other.bit_length()):
            if set_bit := 1 << x & other:
                mask &= self.__exclusives__[set_bit]
        return mask

    def __handle_conflict_lhs__(self, other: int) -> int:
        """Handle conflicts using LHS (left-hand side) resolution strategy.

        In LHS mode, when conflicting flags are combined, the left-hand side
        (existing) value wins and conflicting new values are discarded.

        Args:
            other: Integer value containing the new flag(s) being combined (ignored
                for conflict resolution, but may be used for validation).

        Returns:
            Bitmask that preserves the current (LHS) value and excludes conflicts.

        Example:
            If flag A conflicts with flag B, then A | B results in A.
        """
        return self.__handle_conflict_rhs__(self)

    def __handle_conflict_strict__(self, other: int) -> int:
        """Handle conflicts using STRICT mode - raise ValueError on any conflicts.

        In STRICT mode, any attempt to combine conflicting flags raises a
        ValueError with a detailed message describing all conflicts found.

        Args:
            other: Integer value containing the new flag(s) being combined.

        Returns:
            Always returns -1 if no conflicts are found (allowing the operation).

        Raises:
            ValueError: If any conflicts are detected between the current flags
                and the new flags being combined.

        Example:
            If flag A conflicts with flag B, then A | B raises ValueError.
        """
        other = int(other)
        conflicting_strs: list[str] = []

        for x in range(self.value.bit_length()):
            if (set_bit := 1 << x & self.value) and (
                conflicting_value := other & ~self.__exclusives__[set_bit]
            ):
                conflicting_strs.append(
                    f"{Enum.__new__(self.__class__, conflicting_value)!r} conflicts with {Enum.__new__(self.__class__, set_bit)!r}"
                )

        match len(conflicting_strs):
            case 0:
                return -1
            case 1:
                error_str = conflicting_strs[0]
            case 2:
                error_str = " and ".join(conflicting_strs)
            case _:
                final_conflict_str = conflicting_strs.pop(-1)
                conflicting_strs.append("")
                error_str = ", ".join(conflicting_strs)
                error_str += f"and {final_conflict_str}"
        raise ValueError(error_str)

    def __or__(self, other: int) -> Self:
        """Perform bitwise OR operation with conflict resolution.

        Args:
            other: Integer value to combine with this flag.

        Returns:
            New ExFlag instance with the combined value after conflict resolution.
        """
        return self.__class__(int.__or__(self.value, other) & self._handle_conflict(other))

    def __xor__(self, other: int) -> Self:
        """Perform bitwise XOR operation with conflict resolution.

        Args:
            other: Integer value to XOR with this flag.

        Returns:
            New ExFlag instance with the XOR result after conflict resolution.
        """
        return self.__class__(int.__xor__(self.value, other) & self._handle_conflict(other))

    __ror__ = __or__
    __rxor__ = __xor__


class OptionsFlag(ExFlag):
    """An ExFlag subclass designed for command-line options with rich member definitions.

    OptionsFlag extends ExFlag to support command-line option scenarios where flags
    need aliases, help text, and exclusion relationships. Each flag is defined with
    a tuple containing the value, optional aliases, help text, and optional exclusions.

    The class automatically creates properties for accessing help text and aliases,
    making it suitable for building command-line parsers and help systems.

    Attributes:
        help: Property providing read-only access to the flag's help text.
        aliases: Property providing read-only access to the flag's aliases.

    Examples:
        Basic usage with help text and aliases:
            >>> class MyOptions(OptionsFlag):
            ...     VERBOSE = 1, ["v", "verbose"], "Enable verbose output"
            ...     QUIET = 2, ["q", "quiet"], "Enable quiet mode", [VERBOSE]
            >>> opt = MyOptions.VERBOSE
            >>> opt.help
            'Enable verbose output'
            >>> opt.aliases
            ['v', 'verbose']

        Tuple format variations:
            - (help_str,) - Just help text
            - ([aliases], help_str) - Aliases and help text
            - ([aliases], help_str, [exclusions]) - Full specification
            - (help_str, [exclusions]) - Help and exclusions without aliases
    """

    @property
    def help(self) -> str:
        """Get the help text for this flag.

        Returns:
            The help text string provided during flag definition, or empty
            string if no help text was provided.
        """
        return getattr(self, "_help", "")

    @property
    def aliases(self) -> list[str]:
        """Get the list of aliases for this flag.

        Returns:
            List of string aliases that can be used to reference this flag.
            Returns empty list if no aliases were defined or if the enum
            doesn't have a value-to-member mapping.

        Note:
            Aliases are automatically registered with the enum's internal
            _value2member_map_ when the flag is created.
        """
        if not hasattr(self.__class__, "_value2member_map_"):
            return []

        # Find all string keys that map to this member (excluding the numeric value)
        aliases = [
            key
            for key, member in self.__class__._value2member_map_.items()
            if member is self and isinstance(key, str)
        ]
        return aliases

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an OptionsFlag instance.

        Args:
            *args: Variable positional arguments passed to parent class.
            **kwargs: Variable keyword arguments passed to parent class.

        Note:
            This initializer primarily exists to satisfy type checkers by
            declaring the _help attribute that gets set during __new__.
        """
        # Make the type checkers happy
        self._help: str
        super().__init__(*args, **kwargs)

    def __new__(cls: type["OptionsFlag"], value: int, *args: Any) -> Self:
        """Create new OptionsFlag members with help text, aliases, and exclusions.

        Parses the arguments tuple to extract help text, optional aliases, and
        optional exclusion relationships. The tuple format is flexible to support
        various common patterns for defining command-line options.

        Args:
            cls: The OptionsFlag class being instantiated.
            value: Integer value for this flag.
            *args: Variable arguments in one of these formats:
                - (help_str,) - Just help text
                - ([aliases], help_str) - Aliases list and help text
                - ([aliases], help_str, [exclusions]) - Full specification
                - (help_str, [exclusions]) - Help text and exclusions

        Returns:
            New OptionsFlag instance with help text, aliases, and exclusions configured.

        Raises:
            TypeError: If no help string is provided or too many arguments are given.

        Example:
            >>> class MyOptions(OptionsFlag):
            ...     VERBOSE = 1, ["v", "verbose"], "Enable verbose output"
            ...     QUIET = 2, "Enable quiet mode", [VERBOSE]
        """
        # Parse args tuple.  It can be:
        # (help_str,)
        # ([aliases], help_str)
        # ([aliases], help_str, [exclusive_flags])
        # (help_str, [exclusive_flags])
        exclusions: list[int | tuple[int | Any, ...]] = []
        aliases: list[str] = []
        if not args:
            raise TypeError("A help string is required")  # noqa: TRY003
        elif len(args) == 1:
            help_str: str = args[0]
        elif len(args) == 2:
            # Is the string first or second?
            if isinstance(args[0], str):
                help_str, exclusions = args
            else:
                aliases, help_str = args
        elif len(args) == 3:
            aliases, help_str, exclusions = args
        else:
            raise TypeError(f"Expected at most 4 arguments, received {len(args) + 1}")  # noqa: TRY003
        self: Self = super().__new__(cls, value, exclusions)
        self._help = help_str
        for alias in aliases:
            self._add_value_alias_(alias)  # pyright: ignore[reportAttributeAccessIssue]
        return self
