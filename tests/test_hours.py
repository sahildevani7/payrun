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
