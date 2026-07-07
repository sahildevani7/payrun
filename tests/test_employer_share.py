from decimal import Decimal

from payrun.money import Money
from payrun.rate import Rate
from payrun.statutory.employer import employer_share


def test_full_match_equals_employee_contribution():
    share = employer_share(Money(Decimal("100.00"), "USD"), Rate(Decimal("1.0")))
    assert share == Money(Decimal("100.00"), "USD")


def test_partial_multiplier_scales_down():
    share = employer_share(Money(Decimal("100.00"), "USD"), Rate(Decimal("0.5")))
    assert share == Money(Decimal("50.00"), "USD")


def test_multiplier_above_one_scales_up():
    share = employer_share(Money(Decimal("100.00"), "USD"), Rate(Decimal("1.4")))
    assert share == Money(Decimal("140.00"), "USD")


def test_zero_multiplier_produces_zero_share():
    share = employer_share(Money(Decimal("100.00"), "USD"), Rate.zero())
    assert share == Money.zero("USD")


def test_rounds_half_up_to_the_cent():
    share = employer_share(Money(Decimal("10.005"), "USD"), Rate(Decimal("1.0")))
    assert share == Money(Decimal("10.01"), "USD")
