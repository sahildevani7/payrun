from decimal import Decimal

import pytest

from payrun.errors import ValidationError
from payrun.money import Money
from payrun.reporting.formatting import sum_amounts


def test_sums_a_single_amount():
    assert sum_amounts([Money(Decimal("10.00"), "USD")]) == Money(Decimal("10.00"), "USD")


def test_sums_multiple_amounts():
    amounts = [Money(Decimal("10.00"), "USD"), Money(Decimal("5.50"), "USD")]
    assert sum_amounts(amounts) == Money(Decimal("15.50"), "USD")


def test_rejects_empty_iterable():
    with pytest.raises(ValidationError):
        sum_amounts([])


def test_preserves_currency():
    assert sum_amounts([Money(Decimal("10.00"), "CAD")]).currency == "CAD"


def test_accepts_a_generator_not_just_a_list():
    def gen():
        yield Money(Decimal("1.00"), "USD")
        yield Money(Decimal("2.00"), "USD")

    assert sum_amounts(gen()) == Money(Decimal("3.00"), "USD")
