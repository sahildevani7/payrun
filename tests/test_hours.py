from decimal import Decimal

import pytest

from payrun.errors import ValidationError
from payrun.hours import Hours


def test_accepts_quarter_hour_multiples():
    assert Hours(Decimal("7.75")).value == Decimal("7.75")


def test_rejects_non_quarter_increment():
    with pytest.raises(ValidationError):
        Hours(Decimal("7.10"))


def test_rejects_negative_hours():
    with pytest.raises(ValidationError):
        Hours(Decimal("-0.25"))


def test_rejects_non_decimal_value():
    with pytest.raises(ValidationError):
        Hours(7.5)  # type: ignore[arg-type]


def test_addition_and_subtraction_stay_quarter_hours():
    total = Hours(Decimal("7.75")) + Hours(Decimal("0.25"))
    assert total == Hours(Decimal("8.00"))
    assert total - Hours(Decimal("8.00")) == Hours.zero()


def test_subtraction_below_zero_raises():
    with pytest.raises(ValidationError):
        Hours(Decimal("1.00")) - Hours(Decimal("2.00"))


def test_multiplication_by_decimal_returns_decimal():
    result = Hours(Decimal("8.00")) * Decimal("32.50")
    assert result == Decimal("260.00")


def test_multiplication_rejects_float():
    with pytest.raises(ValidationError):
        Hours(Decimal("8.00")) * 32.5  # type: ignore[arg-type]


def test_ordering_and_hashing():
    assert Hours(Decimal("7.75")) < Hours(Decimal("8.00"))
    assert hash(Hours(Decimal("8.00"))) == hash(Hours(Decimal("8.00")))


def test_zero_is_a_valid_quarter_hour():
    assert Hours.zero().value == Decimal("0")


def test_repr_shows_the_value():
    assert repr(Hours(Decimal("8.00"))) == "Hours(Decimal('8.00'))"


def test_str_shows_the_bare_decimal():
    assert str(Hours(Decimal("8.00"))) == "8.00"


def test_le_and_ge_boundaries():
    assert Hours(Decimal("8.00")) <= Hours(Decimal("8.00"))
    assert Hours(Decimal("8.00")) >= Hours(Decimal("8.00"))


def test_not_equal_to_non_hours():
    assert Hours(Decimal("8.00")) != Decimal("8.00")


def test_quarter_and_half_and_three_quarter_increments_are_accepted():
    assert Hours(Decimal("0.25")).value == Decimal("0.25")
    assert Hours(Decimal("0.50")).value == Decimal("0.50")
    assert Hours(Decimal("0.75")).value == Decimal("0.75")
