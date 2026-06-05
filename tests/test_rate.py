from decimal import Decimal

import pytest

from payrun.errors import ValidationError
from payrun.money import Money
from payrun.rate import Rate


def test_from_percent_converts_to_fraction():
    rate = Rate.from_percent(Decimal("6.2"))
    assert rate.value == Decimal("0.062")


def test_rejects_non_decimal_value():
    with pytest.raises(ValidationError):
        Rate(0.1)  # type: ignore[arg-type]


def test_rejects_negative_value():
    with pytest.raises(ValidationError):
        Rate(Decimal("-0.01"))


def test_of_returns_exact_unrounded_amount():
    rate = Rate(Decimal("0.1"))
    money = Money(Decimal("10.005"), "USD")
    assert rate.of(money) == Decimal("1.0005")


def test_zero_rate_of_any_money_is_zero():
    assert Rate.zero().of(Money(Decimal("500.00"), "USD")) == Decimal("0")


def test_equality_and_ordering():
    assert Rate(Decimal("0.05")) == Rate(Decimal("0.05"))
    assert Rate(Decimal("0.05")) < Rate(Decimal("0.10"))
    assert Rate(Decimal("0.10")) >= Rate(Decimal("0.10"))


def test_rate_is_hashable():
    assert hash(Rate(Decimal("0.05"))) == hash(Rate(Decimal("0.05")))
