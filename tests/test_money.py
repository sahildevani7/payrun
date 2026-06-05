from decimal import Decimal

import pytest

from payrun.errors import CurrencyMismatchError, ValidationError
from payrun.money import Money, allocate
from payrun.rounding import RoundingMode


def test_construction_rejects_float():
    with pytest.raises(ValidationError):
        Money(1.5, "USD")  # type: ignore[arg-type]


def test_construction_rejects_unknown_currency():
    with pytest.raises(ValidationError):
        Money(Decimal("1.00"), "ZZZ")


def test_addition_of_same_currency():
    total = Money(Decimal("1.50"), "USD") + Money(Decimal("2.25"), "USD")
    assert total == Money(Decimal("3.75"), "USD")


def test_addition_across_currency_raises():
    with pytest.raises(CurrencyMismatchError):
        Money(Decimal("1.00"), "USD") + Money(Decimal("1.00"), "CAD")


def test_subtraction_and_negation():
    result = Money(Decimal("5.00"), "USD") - Money(Decimal("2.00"), "USD")
    assert result == Money(Decimal("3.00"), "USD")
    assert -result == Money(Decimal("-3.00"), "USD")


def test_multiplication_by_int_and_decimal():
    base = Money(Decimal("2.00"), "USD")
    assert base * 3 == Money(Decimal("6.00"), "USD")
    assert base * Decimal("1.5") == Money(Decimal("3.00"), "USD")
    assert 3 * base == Money(Decimal("6.00"), "USD")


def test_multiplication_rejects_float_and_bool():
    base = Money(Decimal("2.00"), "USD")
    with pytest.raises(ValidationError):
        base * 1.5  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        base * True  # type: ignore[arg-type]


def test_ordering_requires_same_currency():
    with pytest.raises(CurrencyMismatchError):
        _ = Money(Decimal("1.00"), "USD") < Money(Decimal("1.00"), "CAD")
    assert Money(Decimal("1.00"), "USD") < Money(Decimal("2.00"), "USD")


def test_rounded_uses_currency_exponent():
    unrounded = Money(Decimal("1.005"), "USD")
    assert unrounded.rounded(RoundingMode.HALF_UP) == Money(Decimal("1.01"), "USD")
    assert unrounded.rounded(RoundingMode.HALF_EVEN) == Money(Decimal("1.00"), "USD")


def test_jpy_has_zero_exponent():
    yen = Money(Decimal("104"), "JPY")
    assert yen.exponent == 0
    assert yen.to_minor_units() == 104


def test_to_minor_units_rejects_unrounded_amount():
    with pytest.raises(ValidationError):
        Money(Decimal("1.005"), "USD").to_minor_units()


def test_from_minor_units_round_trips():
    money = Money.from_minor_units(150, "USD")
    assert money == Money(Decimal("1.50"), "USD")
    assert money.to_minor_units() == 150


def test_hash_and_equality_are_consistent():
    a = Money(Decimal("1.00"), "USD")
    b = Money(Decimal("1.00"), "USD")
    assert a == b
    assert hash(a) == hash(b)
    assert a != Money(Decimal("1.00"), "CAD")


def test_zero_is_additive_identity():
    value = Money(Decimal("4.20"), "USD")
    assert value + Money.zero("USD") == value


def test_allocate_splits_exactly_with_no_leftover_cent():
    total = Money(Decimal("10.00"), "USD")
    shares = allocate(total, [1, 1, 1])
    assert sum((s.amount for s in shares), Decimal(0)) == Decimal("10.00")
    assert sorted(s.amount for s in shares) == [Decimal("3.33"), Decimal("3.33"), Decimal("3.34")]


def test_allocate_gives_remainder_to_largest_fraction_first():
    total = Money(Decimal("100.00"), "USD")
    shares = allocate(total, [1, 1, 1])
    amounts = [s.amount for s in shares]
    assert amounts[0] == Decimal("33.34")
    assert amounts[1] == Decimal("33.33")
    assert amounts[2] == Decimal("33.33")


def test_allocate_ties_break_by_ascending_index():
    total = Money(Decimal("0.03"), "USD")
    shares = allocate(total, [1, 1, 1])
    assert [s.amount for s in shares] == [Decimal("0.01")] * 3


def test_allocate_weighted_by_unequal_shares():
    total = Money(Decimal("10.00"), "USD")
    shares = allocate(total, [1, 3])
    assert shares[0] == Money(Decimal("2.50"), "USD")
    assert shares[1] == Money(Decimal("7.50"), "USD")


def test_allocate_preserves_currency():
    total = Money(Decimal("10.00"), "CAD")
    shares = allocate(total, [1, 1])
    assert all(s.currency == "CAD" for s in shares)


def test_allocate_rejects_empty_weights():
    with pytest.raises(ValidationError):
        allocate(Money(Decimal("1.00"), "USD"), [])


def test_allocate_rejects_negative_weights():
    with pytest.raises(ValidationError):
        allocate(Money(Decimal("1.00"), "USD"), [1, -1])


def test_allocate_rejects_all_zero_weights():
    with pytest.raises(ValidationError):
        allocate(Money(Decimal("1.00"), "USD"), [0, 0])


def test_allocate_single_weight_returns_whole_total():
    total = Money(Decimal("7.77"), "USD")
    shares = allocate(total, [1])
    assert shares == [total]
