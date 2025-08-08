import pytest

from highlander import LHS, STRICT, ExFlag


class MyFlag(ExFlag):
    A = 1
    B = 2, [A]
    C = 4


class MyLHSFlag(ExFlag, conflict=LHS):
    A = 1
    B = 2, [A]
    C = 4


class MyStrictFlag(ExFlag, conflict=STRICT):
    A = 1
    B = 2, [A]
    C = 4


class MultiGroupFlag(ExFlag):
    """Test flag with two independent exclusion groups of 4+ members each"""

    # Color group (values 1, 2, 4, 8)
    RED = 1
    GREEN = 2
    BLUE = 4
    YELLOW = 8, [RED, GREEN, BLUE]

    # Size group (values 16, 32, 64, 128, 256)
    TINY = 16
    SMALL = 32
    MEDIUM = 64
    LARGE = 128
    HUGE = 256, [TINY, SMALL, MEDIUM, LARGE]

    # Independent flag that doesn't conflict with either group
    SPECIAL = 512


class StrictTestFlag(ExFlag, conflict=STRICT):
    """Test flag with four exclusion groups to thoroughly test __handle_conflict_strict__"""

    # Group A: Primary colors (1, 2, 4, 8)
    A1_RED = 1
    A2_GREEN = (2,)
    A3_BLUE = (4,)
    A4_YELLOW = 8, [A1_RED, A2_GREEN, A3_BLUE]

    # Group B: Sizes (16, 32, 64, 128)
    B1_SMALL = 16
    B2_MEDIUM = (32,)
    B3_LARGE = (64,)
    B4_HUGE = 128, [B1_SMALL, B2_MEDIUM, B3_LARGE]

    # Group C: Shapes (256, 512, 1024)
    C1_CIRCLE = 256
    C2_SQUARE = (512,)
    C3_TRIANGLE = 1024, [C1_CIRCLE, C2_SQUARE]

    # Group D: Materials (2048, 4096)
    D1_METAL = 2048
    D2_PLASTIC = 4096, [D1_METAL]

    # Independent flags (no conflicts)
    SPECIAL = 8192
    EXTRA = 16384


def test_mutually_exclusive_flag_creation():
    """Test basic ExFlag creation"""

    # Test that flags are created correctly
    assert MyFlag.A == MyFlag.A
    assert MyFlag.B == MyFlag.B
    assert MyFlag.C == MyFlag.C


def test_access_by_name():
    assert MyFlag("A") == MyFlag.A
    with pytest.raises(ValueError, match="is not a valid"):
        MyFlag("invalid_name")


def test_mutually_exclusive_or_operations():
    """Test ExFlag operations with simple cases"""

    assert MyFlag.A | MyFlag.B == 2
    assert MyFlag.B | MyFlag.A == 1
    assert MyFlag.A | MyFlag.C == 5
    assert MyFlag.B | MyFlag.C == 6
    assert MyFlag.A | (MyFlag.B | MyFlag.C) == 6


def test_mutually_exclusive_xor_operations():
    """Test ExFlag operations with simple cases"""

    assert MyFlag.A ^ MyFlag.B == 2
    assert MyFlag.B ^ MyFlag.A == 1
    assert MyFlag.A ^ MyFlag.C == 5
    assert MyFlag.B ^ MyFlag.C == 6
    assert (MyFlag.A | MyFlag.C) ^ (MyFlag.B | MyFlag.C) == 2


def test_invalid_flag_creation():
    """Test invalid flag creation"""
    assert MyFlag(3) == MyFlag.A  # 3 = A+B with conflict resolves to A
    assert MyFlag(6) == MyFlag.B | MyFlag.C  # 6 = B+C with no conflict remains B+C (value 6)


def test_lhs_flag_creation():
    """Test LHSFlag creation"""
    # Test that flags are created correctly
    assert MyLHSFlag.A == MyLHSFlag.A
    assert MyLHSFlag.B == MyLHSFlag.B
    assert MyLHSFlag.C == MyLHSFlag.C


def test_lhs_flag_operations():
    """Test LHSFlag operations with LHS conflict resolution"""
    # LHS resolution: left-hand side wins in conflicts
    assert MyLHSFlag.A | MyLHSFlag.B == 1  # A wins (LHS)
    assert MyLHSFlag.B | MyLHSFlag.A == 2  # B wins (LHS)
    assert MyLHSFlag.A | MyLHSFlag.C == 5  # No conflict
    assert MyLHSFlag.B | MyLHSFlag.C == 6  # No conflict
    assert MyLHSFlag.A | (MyLHSFlag.B | MyLHSFlag.C) == 5  # A wins over B, plus C


def test_lhs_flag_creation_with_conflicts():
    """Test LHSFlag creation with conflicts"""
    assert MyLHSFlag(3) == MyLHSFlag.A  # 3 = A+B with conflict resolves to A (value 1)
    assert (
        MyLHSFlag(6) == MyLHSFlag.B | MyLHSFlag.C
    )  # 6 = B+C with no conflict remains B+C (value 6)


def test_strict_flag_creation():
    """Test StrictFlag creation"""
    # Test that flags are created correctly
    assert MyStrictFlag.A == MyStrictFlag.A
    assert MyStrictFlag.B == MyStrictFlag.B
    assert MyStrictFlag.C == MyStrictFlag.C


def test_strict_flag_operations():
    """Test StrictFlag operations with strict conflict resolution"""
    # Strict resolution: raises ValueError on conflicts
    with pytest.raises(ValueError, match="conflicts with"):
        MyStrictFlag.A | MyStrictFlag.B

    with pytest.raises(ValueError, match="conflicts with"):
        MyStrictFlag.B | MyStrictFlag.A

    # No conflicts between A/B and C
    assert MyStrictFlag.A | MyStrictFlag.C == 5
    assert MyStrictFlag.B | MyStrictFlag.C == 6


def test_strict_flag_creation_with_conflicts():
    """Test StrictFlag creation with conflicts"""
    # Should raise ValueError when creating conflicting combinations
    with pytest.raises(ValueError, match="conflicts with"):
        MyStrictFlag(3)  # 3 = A+B with conflict should raise


def test_multiple_exclusion_groups():
    """Test ExFlag with two independent exclusion groups of 4+ members each"""

    # Test basic flag creation and values
    assert MultiGroupFlag.RED.value == 1
    assert MultiGroupFlag.GREEN.value == 2
    assert MultiGroupFlag.BLUE.value == 4
    assert MultiGroupFlag.YELLOW.value == 8
    assert MultiGroupFlag.TINY.value == 16
    assert MultiGroupFlag.SMALL.value == 32
    assert MultiGroupFlag.MEDIUM.value == 64
    assert MultiGroupFlag.LARGE.value == 128
    assert MultiGroupFlag.HUGE.value == 256
    assert MultiGroupFlag.SPECIAL.value == 512

    # Test exclusions within color group (RHS wins)
    assert MultiGroupFlag.RED | MultiGroupFlag.GREEN == MultiGroupFlag.GREEN  # 2
    assert MultiGroupFlag.GREEN | MultiGroupFlag.BLUE == MultiGroupFlag.BLUE  # 4
    assert MultiGroupFlag.BLUE | MultiGroupFlag.YELLOW == MultiGroupFlag.YELLOW  # 8
    assert MultiGroupFlag.YELLOW | MultiGroupFlag.RED == MultiGroupFlag.RED  # 1

    # Test exclusions within size group (RHS wins)
    assert MultiGroupFlag.TINY | MultiGroupFlag.SMALL == MultiGroupFlag.SMALL  # 32
    assert MultiGroupFlag.SMALL | MultiGroupFlag.MEDIUM == MultiGroupFlag.MEDIUM  # 64
    assert MultiGroupFlag.MEDIUM | MultiGroupFlag.LARGE == MultiGroupFlag.LARGE  # 128
    assert MultiGroupFlag.LARGE | MultiGroupFlag.HUGE == MultiGroupFlag.HUGE  # 256
    assert MultiGroupFlag.HUGE | MultiGroupFlag.TINY == MultiGroupFlag.TINY  # 16

    # Test combinations across different groups (no conflicts)
    assert MultiGroupFlag.RED | MultiGroupFlag.TINY == 17  # 1 + 16
    assert MultiGroupFlag.GREEN | MultiGroupFlag.SMALL == 34  # 2 + 32
    assert MultiGroupFlag.BLUE | MultiGroupFlag.MEDIUM == 68  # 4 + 64
    assert MultiGroupFlag.YELLOW | MultiGroupFlag.LARGE == 136  # 8 + 128

    # Test with independent SPECIAL flag
    assert MultiGroupFlag.RED | MultiGroupFlag.SPECIAL == 513  # 1 + 512
    assert MultiGroupFlag.TINY | MultiGroupFlag.SPECIAL == 528  # 16 + 512
    assert MultiGroupFlag.RED | MultiGroupFlag.TINY | MultiGroupFlag.SPECIAL == 529  # 1 + 16 + 512

    # Test XOR operations within color group (RHS wins)
    assert MultiGroupFlag.RED ^ MultiGroupFlag.GREEN == MultiGroupFlag.GREEN  # 2
    assert MultiGroupFlag.GREEN ^ MultiGroupFlag.BLUE == MultiGroupFlag.BLUE  # 4
    assert MultiGroupFlag.BLUE ^ MultiGroupFlag.YELLOW == MultiGroupFlag.YELLOW  # 8

    # Test XOR operations within size group (RHS wins)
    assert MultiGroupFlag.TINY ^ MultiGroupFlag.SMALL == MultiGroupFlag.SMALL  # 32
    assert MultiGroupFlag.SMALL ^ MultiGroupFlag.MEDIUM == MultiGroupFlag.MEDIUM  # 64
    assert MultiGroupFlag.MEDIUM ^ MultiGroupFlag.LARGE == MultiGroupFlag.LARGE  # 128

    # Test XOR operations across different groups (no conflicts)
    assert MultiGroupFlag.RED ^ MultiGroupFlag.TINY == 17  # 1 ^ 16 = 17
    assert MultiGroupFlag.GREEN ^ MultiGroupFlag.SMALL == 34  # 2 ^ 32 = 34
    assert MultiGroupFlag.BLUE ^ MultiGroupFlag.MEDIUM == 68  # 4 ^ 64 = 68

    # Test enum creation with conflicting values from same group
    # Color group conflicts (RED + GREEN = 3)
    result1 = MultiGroupFlag(3)  # RED + GREEN should resolve to RED
    assert result1 == MultiGroupFlag.RED
    assert result1.value == 1

    # Size group conflicts (TINY + SMALL = 48)
    result2 = MultiGroupFlag(48)  # TINY + SMALL should resolve to TINY
    assert result2 == MultiGroupFlag.TINY
    assert result2.value == 16

    # Multiple conflicts within color group (RED + GREEN + BLUE = 7)
    result3 = MultiGroupFlag(7)  # Should resolve to RED
    assert result3 == MultiGroupFlag.RED
    assert result3.value == 1

    # Multiple conflicts within size group (TINY + SMALL + MEDIUM = 112)
    result4 = MultiGroupFlag(112)  # Should resolve to TINY
    assert result4 == MultiGroupFlag.TINY
    assert result4.value == 16

    # Conflicts from both groups (RED + GREEN + TINY + SMALL = 51)
    result5 = MultiGroupFlag(51)  # Should resolve conflicts in both groups to RED + TINY
    assert result5.value == 17  # RED (1) + TINY (16)

    # Complex combination with SPECIAL flag (RED + GREEN + SPECIAL = 515)
    result6 = MultiGroupFlag(515)  # Should resolve to RED + SPECIAL (GREEN conflicts with RED)
    assert result6.value == 513  # RED (1) + SPECIAL (512)

    # Test case with flags from both groups plus SPECIAL (RED + TINY + SPECIAL = 529)
    result7 = MultiGroupFlag(529)  # Should remain as is since no conflicts
    assert result7.value == 529  # RED (1) + TINY (16) + SPECIAL (512)

    # Test case with conflicts in both groups plus SPECIAL (RED + GREEN + TINY + SMALL + SPECIAL = 563)
    result8 = MultiGroupFlag(563)  # Should resolve to RED + TINY + SPECIAL
    assert result8.value == 529  # RED (1) + TINY (16) + SPECIAL (512)


def test_strict_conflict_handling():
    """Comprehensive test for __handle_conflict_strict__ covering all code paths"""

    # Test Case 0: No conflicts (should not raise, operations should work normally)
    # Operations between independent flags and across different groups
    assert StrictTestFlag.A1_RED | StrictTestFlag.B1_SMALL == 17  # 1 + 16
    assert StrictTestFlag.C1_CIRCLE | StrictTestFlag.D1_METAL == 2304  # 256 + 2048
    assert StrictTestFlag.SPECIAL | StrictTestFlag.EXTRA == 24576  # 8192 + 16384

    # Operations within same group that don't conflict yet
    assert StrictTestFlag.A1_RED | StrictTestFlag.SPECIAL == 8193  # 1 + 8192
    assert StrictTestFlag.B1_SMALL | StrictTestFlag.C1_CIRCLE == 272  # 16 + 256

    # Test Case 1: Single conflict (simple error message)
    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.A1_RED | StrictTestFlag.A2_GREEN  # RED conflicts with GREEN

    error_msg = str(exc_info.value)
    # Should contain single conflict message without "and"
    assert "conflicts with" in error_msg
    assert " and " not in error_msg
    assert error_msg.count("conflicts with") == 1

    # Another single conflict case
    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.B1_SMALL | StrictTestFlag.B2_MEDIUM  # SMALL conflicts with MEDIUM

    error_msg = str(exc_info.value)
    assert "conflicts with" in error_msg
    assert " and " not in error_msg
    assert error_msg.count("conflicts with") == 1

    # Test Case 2: Two conflicts (join with " and ")
    with pytest.raises(ValueError, match=r".*conflicts with.*and.*conflicts with.*") as exc_info:
        # This creates a flag with two bits set that each conflict with other flags
        # We need to create a composite flag that has conflicts in multiple positions
        combined = StrictTestFlag.A1_RED | StrictTestFlag.B1_SMALL  # 1 + 16 = 17
        combined | (StrictTestFlag.A2_GREEN | StrictTestFlag.B2_MEDIUM)  # Add conflicting flags

    error_msg = str(exc_info.value)
    # Should contain exactly two conflicts joined with " and "
    assert "conflicts with" in error_msg
    assert " and " in error_msg
    assert error_msg.count("conflicts with") == 2

    # Test Case 3+: Three or more conflicts (comma-separated with final "and")
    with pytest.raises(ValueError, match=r".*conflicts with.*,.*and.*conflicts with.*") as exc_info:
        # Create a flag with multiple conflicting bits
        combined = (
            StrictTestFlag.A1_RED | StrictTestFlag.B1_SMALL | StrictTestFlag.C1_CIRCLE
        )  # 1 + 16 + 256 = 273
        # Add multiple conflicting flags: GREEN (conflicts with RED), MEDIUM (conflicts with SMALL), SQUARE (conflicts with CIRCLE)
        combined | (StrictTestFlag.A2_GREEN | StrictTestFlag.B2_MEDIUM | StrictTestFlag.C2_SQUARE)

    error_msg = str(exc_info.value)
    # Should contain three conflicts with comma separation and final "and"
    assert "conflicts with" in error_msg
    assert "," in error_msg  # Should have comma separation
    assert "and" in error_msg  # Should have final "and"
    assert error_msg.count("conflicts with") >= 3

    # Test edge case: Operations that succeed (no conflicts detected)
    # Independent flags should not cause conflicts
    result1 = StrictTestFlag.SPECIAL | StrictTestFlag.EXTRA
    assert result1.value == 24576  # 8192 + 16384

    # Flags from different groups should not conflict
    result2 = (
        StrictTestFlag.A1_RED
        | StrictTestFlag.B1_SMALL
        | StrictTestFlag.C1_CIRCLE
        | StrictTestFlag.D1_METAL
    )
    assert result2.value == 2321  # 1 + 16 + 256 + 2048

    # Test XOR operations also trigger strict checking
    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.A1_RED ^ StrictTestFlag.A2_GREEN

    error_msg = str(exc_info.value)
    assert "conflicts with" in error_msg

    # Test complex exclusions within groups
    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.A4_YELLOW | StrictTestFlag.A1_RED  # YELLOW excludes RED, GREEN, BLUE

    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.B4_HUGE | StrictTestFlag.B1_SMALL  # HUGE excludes SMALL, MEDIUM, LARGE

    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.C3_TRIANGLE | StrictTestFlag.C1_CIRCLE  # TRIANGLE excludes CIRCLE, SQUARE

    with pytest.raises(ValueError, match=r".*conflicts with.*") as exc_info:
        StrictTestFlag.D2_PLASTIC | StrictTestFlag.D1_METAL  # PLASTIC excludes METAL


def test_add_exclusions_method():
    """Test the add_exclusions instance method for coverage"""

    # Create a simple flag class to test add_exclusions
    class TestFlag(ExFlag):
        A = 1
        B = 2
        C = 4
        D = 8

    # Test add_exclusions method
    flag_a = TestFlag.A
    flag_a.add_exclusions(TestFlag.B, TestFlag.C)

    # After adding exclusions, the exclusives mask should be updated
    assert TestFlag.__exclusives__[1] != -1  # A should have exclusions
    assert TestFlag.__exclusives__[2] != -1  # B should exclude A
    assert TestFlag.__exclusives__[4] != -1  # C should exclude A

    # A + B should resolve to A (cleaned_value becomes 1 due to exclusions)
    result = TestFlag(3)  # A + B
    assert result == TestFlag.A

    # Test with integer values
    flag_d = TestFlag.D
    flag_d.add_exclusions(4)  # Exclude C by value

    # Check that exclusions were set up
    assert TestFlag.__exclusives__[8] != -1  # D should exclude C
    assert TestFlag.__exclusives__[4] != -1  # C should exclude D

    # Test with mixed values (flags and integers)
    class TestFlag2(ExFlag):
        X = 16
        Y = 32
        Z = 64

    flag_x = TestFlag2.X
    flag_x.add_exclusions(TestFlag2.Y, 64)  # Mix flag and integer

    # Verify exclusions were set up
    assert TestFlag2.__exclusives__[16] != -1  # X should have exclusions
    assert TestFlag2.__exclusives__[32] != -1  # Y should exclude X
    assert TestFlag2.__exclusives__[64] != -1  # Z should exclude X


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
