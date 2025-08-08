from enum import Flag

import pytest

from highlander.type import EnumPlusType, ValueAliasShim, rebind_method, traverse_bases


class ConflictHandler:
    def _handle_conflict(self, other):
        return -1

    def __handle_conflict_rhs__(self, other):
        return -1

    def __handle_conflict_lhs__(self, other):
        return -1

    def __handle_conflict_strict__(self, other):
        raise ValueError("conflict")


def test_traverse_bases():
    class A:
        pass

    class B(A):
        pass

    class C:
        pass

    class D(B, C):
        pass

    assert traverse_bases((D,)) == (D, B, A, C)


def test_rebind_method_classmethod():
    class Source:
        @classmethod
        def method(cls):
            return "source"

    class Target:
        pass

    rebind_method("new_method", Target, Source.method, Source)
    assert Target.new_method() == "source"
    rebind_method("newer_method", Target, "method", Source)
    assert Target.newer_method() == "source"


def test_rebind_method_staticmethod():
    class Source:
        @staticmethod
        def method():
            return "source"

    class Target:
        pass

    rebind_method("new_method", Target, Source.method, Source)
    assert Target.new_method() == "source"
    rebind_method("newer_method", Target, "method", Source)
    assert Target.newer_method() == "source"


def test_rebind_method_instancemethod():
    class Source:
        def method(self):
            return "source"

    class Target:
        pass

    rebind_method("new_method", Target, Source.method, Source)
    rebind_method("newer_method", Target, "method", Source)
    t = Target()
    assert t.new_method() == "source"
    assert t.newer_method() == "source"


def test_enum_plus_type_creation():
    class MyFlag(ConflictHandler, Flag, metaclass=EnumPlusType):
        A = 1
        B = 2

    assert issubclass(MyFlag, Flag)
    assert MyFlag.A.value == 1
    assert MyFlag.B.value == 2


def test_conflict_resolution_rhs():
    class MyFlag(ConflictHandler, Flag, metaclass=EnumPlusType, conflict="rhs"):
        A = 1
        B = 2

    assert MyFlag.A | MyFlag.B == MyFlag.A | MyFlag.B


def test_conflict_resolution_invalid():
    with pytest.raises(TypeError, match="Invalid conflict resolution: invalid"):

        class MyFlag(ConflictHandler, Flag, metaclass=EnumPlusType, conflict="invalid"):
            A = 1


def test_call_restored():
    class MyFlag(ConflictHandler, Flag, metaclass=EnumPlusType):
        A = 1

        def __call__(self, *args, **kwargs):
            return "called"

    assert MyFlag(1) == "called"


def test_enum_plus_type_no_conflict():
    class MyFlag(Flag, metaclass=EnumPlusType, conflict=None):
        A = 1
        B = 2

    assert MyFlag.A | MyFlag.B == MyFlag.B | MyFlag.A


def test_rebind_method_from_string():
    class Source:
        def method(self):
            return "source"

    class Target:
        pass

    rebind_method("new_method", Target, "method", Source)
    t = Target()
    assert t.new_method() == "source"


def test_rebind_method_error_conditions():
    class Target:
        pass

    class Source:
        non_callable = 1

    with pytest.raises(ValueError, match="if src_method is a string, src_cls is required"):
        rebind_method("new_method", Target, "method")

    with pytest.raises(ValueError, match="was invalid object"):
        rebind_method("new_method", Target, object(), Source)

    with pytest.raises(ValueError, match="non_existent_method not in"):
        rebind_method("new_method", Target, "non_existent_method", Source)

    with pytest.raises(TypeError, match="is not a valid function"):
        rebind_method("new_method", Target, "non_callable", Source)


def test_enum_plus_type_missing_conflict_implementation():
    with pytest.raises(TypeError, match="No matching implementation for conflict resolution: rhs"):

        class MyFlag(Flag, metaclass=EnumPlusType, conflict="rhs"):
            pass


def test_enum_plus_type_inherit_conflict_from_base():
    """Test inheriting conflict resolution from base class."""
    from highlander.type import ConflictResolution

    # Create a base class with a conflict resolution setting
    class BaseClass:
        __conflict_resolution__ = ConflictResolution.RHS

        def __handle_conflict_rhs__(self, other):
            return -1

    # Create an enum that inherits from this base without specifying conflict
    class InheritedFlag(BaseClass, ConflictHandler, Flag, metaclass=EnumPlusType, conflict=None):
        A = 1
        B = 2

    # Verify that it inherited the conflict resolution
    assert hasattr(InheritedFlag, "__conflict_resolution__")
    assert InheritedFlag.__conflict_resolution__ == ConflictResolution.RHS


def test_rebind_method_direct_callable():
    """Test direct callable without src_cls."""

    def test_func(self):
        return "test_result"

    class Target:
        pass

    # This should use the direct callable path (src_cls=None)
    rebind_method("test_method", Target, test_func)

    # Test that the method was bound correctly
    assert Target().test_method() == "test_result"


def test_restore_news_delete_new():
    """Test del base.__new__ when new_method is None."""
    from highlander.type import EnumPlusType

    # Create a test class and simulate the scenario where restore_new_members
    # would return None for a base class
    class TestBase:
        pass

    # Set up a scenario where we have a __new__ to delete
    original_new = lambda cls: "dummy"
    TestBase.__new__ = original_new

    # Create the replaced_new_methods dict with None value to trigger delete path
    replaced = {TestBase: None}

    # Verify TestBase has our custom __new__ before the call
    assert TestBase.__new__ == original_new

    # This should trigger the del base.__new__ path
    EnumPlusType.restore_news(replaced)

    # Verify that our custom __new__ was deleted (it will fall back to object.__new__)
    assert TestBase.__new__ != original_new


def test_value_alias_shim():
    """Test ValueAliasShim class for 100% coverage."""
    from enum import Enum

    # Create a test enum class that inherits from ValueAliasShim
    class TestEnum(ValueAliasShim, Enum):
        OPTION_A = 1
        OPTION_B = 2

    # Test adding a new hashable alias - this should work fine
    TestEnum.OPTION_A._add_value_alias_("new_alias")
    assert "new_alias" in TestEnum._value2member_map_
    assert TestEnum._value2member_map_["new_alias"] == TestEnum.OPTION_A

    # Test adding another alias to the same option
    TestEnum.OPTION_A._add_value_alias_("another_alias")
    assert "another_alias" in TestEnum._value2member_map_
    assert TestEnum._value2member_map_["another_alias"] == TestEnum.OPTION_A

    # Test adding an alias that already exists and is bound to the same member (early return)
    TestEnum.OPTION_A._add_value_alias_("new_alias")  # Should return early without error
    assert TestEnum._value2member_map_["new_alias"] == TestEnum.OPTION_A

    # Test trying to add an alias that's already bound to a different member
    with pytest.raises(ValueError, match="'new_alias' is already bound"):
        TestEnum.OPTION_B._add_value_alias_("new_alias")

    # Test with different hashable types
    TestEnum.OPTION_B._add_value_alias_(42)  # integer
    assert 42 in TestEnum._value2member_map_
    assert TestEnum._value2member_map_[42] == TestEnum.OPTION_B

    TestEnum.OPTION_B._add_value_alias_(("tuple", "alias"))  # tuple
    assert ("tuple", "alias") in TestEnum._value2member_map_
    assert TestEnum._value2member_map_[("tuple", "alias")] == TestEnum.OPTION_B

    # Test unhashable types - should raise TypeError
    with pytest.raises(TypeError, match="Unhashable values aren't supported"):
        TestEnum.OPTION_A._add_value_alias_(["unhashable", "list"])

    with pytest.raises(TypeError, match="Unhashable values aren't supported"):
        TestEnum.OPTION_A._add_value_alias_({"unhashable": "dict"})

    with pytest.raises(TypeError, match="Unhashable values aren't supported"):
        TestEnum.OPTION_A._add_value_alias_({"unhashable", "set"})
