from collections.abc import Callable
from enum import Enum, EnumType, StrEnum, auto
from types import FunctionType
from typing import Any


class ConflictResolution(StrEnum):
    """Enumeration defining conflict resolution strategies for mutually exclusive flags.

    This enum defines how Highlander enums should handle conflicts when mutually
    exclusive flags are combined. Each strategy provides different behavior when
    incompatible flags are used together in bitwise operations.

    Attributes:
        RHS: Right-hand side wins. The new value replaces the old value in conflicts.
        LHS: Left-hand side wins. The old value is preserved, new conflicting values are discarded.
        STRICT: Strict mode raises ValueError on any conflicts.

    Examples:
        RHS (Right-hand side wins) - default behavior:
            >>> from highlander import ExFlag
            >>> class F(ExFlag, conflict="rhs"):
            ...     FLAG1 = 1
            ...     EX_FLAG1 = 2
            ...     EX_FLAG2 = 4, [EX_FLAG1]
            >>> value = F.EX_FLAG1
            >>> value |= F.FLAG1 | F.EX_FLAG2
            >>> value == F.FLAG1 | F.EX_FLAG2
            True

        LHS (Left-hand side wins):
            >>> class F(ExFlag, conflict="lhs"):
            ...     FLAG1 = 1
            ...     EX_FLAG1 = 2
            ...     EX_FLAG2 = 4, [EX_FLAG1]
            >>> value = F.EX_FLAG1
            >>> value |= F.FLAG1 | F.EX_FLAG2
            >>> value == F.FLAG1 | F.EX_FLAG1
            True

        STRICT (Raises on conflicts):
            >>> class F(ExFlag, conflict="strict"):
            ...     FLAG1 = 1
            ...     EX_FLAG1 = 2
            ...     EX_FLAG2 = 4, [EX_FLAG1]
            >>> value = F.EX_FLAG1
            >>> value |= F.FLAG1 | F.EX_FLAG2
            Traceback (most recent call last):
            ValueError: F.EX_FLAG1 and F.EX_FLAG2 can't be combined
    """

    RHS = auto()
    LHS = auto()
    STRICT = auto()


class EnumPlusType(EnumType):
    """Metaclass for creating Enum subclasses with support for advanced features.

    Metaclass for creating Enum subclasses with support for advanced features
    such as:
        - Better subclassing by supporting super().__new__.
        - Modify subclasses through __init_subenum__.
        - Control member lookups by implementing __call__.
        - Support for flexible conflict resolution policies.
        - Preservation of bitwise operators.
    """

    def __new__(  # noqa: C901
        metacls: type["EnumPlusType"],
        cls: str,
        bases: tuple[type, ...],
        classdict: dict[str, Any],
        *,
        conflict_enum_cls: type[Enum] = ConflictResolution,
        conflict: Enum | str = ConflictResolution.RHS,
        boundary: Any = None,
        _simple: bool = False,
        **kwds: Any,
    ) -> type:
        """Create a new enum class with exclusive flag support.

        Args:
            metacls: The metaclass being used to create the new class.
            cls: The name of the enum class being created.
            bases: Base classes for the new enum class.
            classdict: Dictionary containing the class attributes and methods.
            conflict_enum_cls: Enum class defining conflict resolution strategies.
            conflict: The conflict resolution strategy to use, either an enum value
                or string that can be converted to one.
            boundary: Boundary handling for flag values (passed to EnumType).
            _simple: Whether this is a simple enum (passed to EnumType).
            **kwds: Additional keyword arguments passed to parent metaclass.

        Returns:
            The newly created enum class with exclusive flag support.

        Raises:
            TypeError: If the conflict resolution strategy is invalid or not implemented.
        """
        conflict_enum: Enum | None
        if conflict:
            try:
                # conflict_enum_cls(conflict) returns an instance of the enum class
                conflict_enum = conflict_enum_cls(conflict)
            except ValueError as err:
                err_msg = f"Invalid conflict resolution: {conflict}"
                raise TypeError(err_msg) from err
        else:
            for base in traverse_bases(bases):
                if conflict_enum := getattr(base, "__conflict_resolution__", None):
                    break
            else:
                conflict_enum = None

        # Search bases for bitwise methods. If they aren't in the classdict, they'll be overwritten with Flag versions.
        for name in (
            "__or__",
            "__and__",
            "__xor__",
            "__ror__",
            "__rand__",
            "__rxor__",
        ):
            if name not in classdict:
                for base in traverse_bases(bases):  # pragma: no cover - this loop will never fail
                    if attr := base.__dict__.get(name):
                        classdict[name] = attr
                        break

        # Preserve __call__. It's used as __new__ in Enums to look up members.
        cls_call: Callable[[type, Any], Any] | None = classdict.pop("__call__", None)

        # Call parent __init_subenum__ methods.
        for base in traverse_bases(bases):
            if hasattr(base, "__init_subenum__"):
                base.__init_subenum__(classdict, **kwds)  # type: ignore[misc]
        # Replace any altered __new__ methods with their originals.
        # EnumType does this, but it stops at the first one found.
        replaced_news = metacls.restore_new_members(bases)
        enum_cls = super().__new__(
            metacls, cls, bases, classdict, boundary=boundary, _simple=_simple, **kwds
        )
        # Restore the replaced __new__ methods.
        metacls.restore_news(replaced_news)

        # Bind the conflict resolution method
        if conflict_enum:
            conflict_attr: Any | None
            for base in enum_cls.__mro__[:-1]:
                if conflict_attr := getattr(
                    base, f"__handle_conflict_{conflict_enum.value}__", None
                ):
                    break
            else:
                raise TypeError(  # noqa: TRY003
                    f"No matching implementation for conflict resolution: {conflict_enum}"
                )
            rebind_method("_handle_conflict", enum_cls, conflict_attr, base)
            enum_cls.__conflict_resolution__ = conflict_enum

        # Restore __call__. If this class doesn't have a __call__, then remove the one inserted by EnumType.
        if cls_call:
            rebind_method("__new__", enum_cls, cls_call)
        else:
            del enum_cls.__new__
        return enum_cls

    @staticmethod
    def restore_new_members(bases: tuple[type, ...]) -> dict[type, Callable[..., Any] | None]:
        """Restore original __new__ methods from __new_member__ attributes.

        This method handles the temporary replacement of __new__ methods during
        enum creation, storing the original methods for later restoration.

        Args:
            bases: Tuple of base classes to examine for __new_member__ attributes.

        Returns:
            Dictionary mapping base classes to their original __new__ methods.
            Values may be None if no original __new__ method existed.
        """
        replaced_new_methods: dict[type, Callable[..., Any] | None] = {}
        for base in traverse_bases(bases):
            if member_attr := base.__dict__.get("__new_member__"):
                # I don't know what weirdness could result in a class with a
                # __new_member__ and no __new__, but we aren't going to deal
                # with it at this level.
                replaced_new_methods[base] = base.__dict__.get("__new__")
                base.__new__ = member_attr
        return replaced_new_methods

    @staticmethod
    def restore_news(replaced_new_methods: dict[type, Callable[..., Any] | None]) -> None:
        """Restore previously saved __new__ methods to their original classes.

        Args:
            replaced_new_methods: Dictionary mapping classes to their original
                __new__ methods that should be restored.
        """
        for base, new_method in replaced_new_methods.items():
            if new_method:
                # __new__ is still at __new_member__, so just overwrite it
                base.__new__ = new_method  # type: ignore[misc] # pyright: ignore[reportAttributeAccessIssue]
            else:
                # Again, not sure how this happened, but it's above our
                # abstraction grade.
                del base.__new__


def traverse_bases(bases: tuple[type, ...]) -> tuple[type, ...]:
    """Traverse base classes to get an ordered list of the inheritance tree.

    This function examines the method resolution order (MRO) of all base classes
    and returns a deduplicated, ordered tuple of all classes in the hierarchy.

    Args:
        bases: Tuple of base classes to traverse.

    Returns:
        Ordered tuple of all classes in the inheritance hierarchy, excluding
        the built-in object class.
    """
    # Use a dict as an ordered set
    base_tree: dict[type, None] = {}

    for super_cls in bases:
        for base in super_cls.__mro__[:-1]:  # skip object
            base_tree[base] = None

    return tuple(base_tree.keys())


def rebind_method(  # noqa: C901
    target_name: str,
    target_cls: type,
    src_method: classmethod | staticmethod | Callable[..., Any] | str,
    src_cls: type | None = None,
) -> None:
    """Rebind a method from one class to another with a new name.

    This function creates a new method on the target class by copying a method
    from a source class or using a provided method object. The new method
    maintains the same functionality but can have a different name.

    Args:
        target_name: The name to give the method in the target class.
        target_cls: The class to which the method should be bound.
        src_method: The source method to copy. Can be:
            - A classmethod or staticmethod decorator
            - A callable function
            - A string name of a method (requires src_cls)
        src_cls: The source class containing the method (required if src_method
            is a string).

    Raises:
        ValueError: If src_method is a string but src_cls is not provided,
            if the method name is not found in src_cls, or if src_method
            is not a valid object.
        TypeError: If src_method is not callable or doesn't have the required
            function attributes.
    """

    if isinstance(src_method, str) and not src_cls:
        raise ValueError("if src_method is a string, src_cls is required")  # noqa: TRY003

    method: classmethod | staticmethod | Callable[..., Any] | None
    if src_cls:
        if isinstance(src_method, str):
            src_method_name: str = src_method
        elif not (src_method_name := getattr(src_method, "__name__", None)):
            raise ValueError(f"{src_method} was invalid object")  # noqa: TRY003

        for base in src_cls.__mro__:
            if method := base.__dict__.get(src_method_name):
                break
        else:
            raise ValueError(f"{src_method_name} not in {src_cls}")  # noqa: TRY003
    else:
        method = src_method  # type: ignore[invalid-assignment] Can't be a str

    if isinstance(method, classmethod | staticmethod):
        func: Callable[..., Any] = method.__func__  # type: ignore[attr-defined]
        bind_method: Callable[[Callable[..., Any]], Any] = type(method)
    else:
        func = method
        bind_method = lambda x: x

    # Ensure func is callable and has the required attributes
    if not callable(func) or not hasattr(func, "__code__"):
        raise TypeError(f"{src_method} is not a valid function")  # noqa: TRY003

    new_func: FunctionType = FunctionType(
        func.__code__,  # type: ignore[attr-defined]
        func.__globals__,  # type: ignore[attr-defined]
        target_name,
        func.__defaults__,  # type: ignore[attr-defined]
        func.__closure__,  # type: ignore[attr-defined]
    )
    new_func.__qualname__ = f"{target_cls.__name__}.{target_name}"

    # Copy additional attributes
    for attr in ("__doc__", "__annotations__"):
        if attr_val := getattr(func, attr, None):
            setattr(new_func, attr, attr_val)

    # Bind to target
    setattr(target_cls, target_name, bind_method(new_func))
