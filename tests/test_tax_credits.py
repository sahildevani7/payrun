from decimal import Decimal

import pytest

from payrun.errors import CurrencyMismatchError
from payrun.money import Money
from payrun.tax.credits import apply_credit, apply_credits


def test_credit_reduces_tax():
    result = apply_credit(Money(Decimal("500.00"), "USD"), Money(Decimal("100.00"), "USD"))
    assert result == Money(Decimal("400.00"), "USD")


def test_credit_larger_than_tax_floors_at_zero():
    result = apply_credit(Money(Decimal("50.00"), "USD"), Money(Decimal("100.00"), "USD"))
    assert result == Money.zero("USD")


def test_credit_equal_to_tax_is_zero():
    result = apply_credit(Money(Decimal("100.00"), "USD"), Money(Decimal("100.00"), "USD"))
    assert result == Money.zero("USD")


def test_zero_credit_leaves_tax_unchanged():
    result = apply_credit(Money(Decimal("500.00"), "USD"), Money.zero("USD"))
    assert result == Money(Decimal("500.00"), "USD")


def test_zero_tax_with_zero_credit_is_zero():
    result = apply_credit(Money.zero("USD"), Money.zero("USD"))
    assert result == Money.zero("USD")


def test_credit_preserves_currency():
    result = apply_credit(Money(Decimal("500.00"), "CAD"), Money(Decimal("100.00"), "CAD"))
    assert result.currency == "CAD"


def test_multiple_credits_are_summed_before_applying():
    result = apply_credits(
        Money(Decimal("500.00"), "USD"),
        Money(Decimal("100.00"), "USD"),
        Money(Decimal("50.00"), "USD"),
    )
    assert result == Money(Decimal("350.00"), "USD")


def test_multiple_credits_floored_at_zero():
    result = apply_credits(
        Money(Decimal("100.00"), "USD"),
        Money(Decimal("100.00"), "USD"),
        Money(Decimal("50.00"), "USD"),
    )
    assert result == Money.zero("USD")


def test_no_credits_leaves_tax_unchanged():
    result = apply_credits(Money(Decimal("500.00"), "USD"))
    assert result == Money(Decimal("500.00"), "USD")


def test_single_credit_matches_apply_credit():
    assert apply_credits(Money(Decimal("500.00"), "USD"), Money(Decimal("100.00"), "USD")) == (
        apply_credit(Money(Decimal("500.00"), "USD"), Money(Decimal("100.00"), "USD"))
    )


def test_mismatched_currency_credits_raise():
    with pytest.raises(CurrencyMismatchError):
        apply_credits(
            Money(Decimal("500.00"), "USD"),
            Money(Decimal("100.00"), "USD"),
            Money(Decimal("50.00"), "CAD"),
        )


def test_apply_credit_delegates_to_apply_credits():
    assert apply_credit(Money(Decimal("500.00"), "USD"), Money(Decimal("150.00"), "USD")) == (
        apply_credits(Money(Decimal("500.00"), "USD"), Money(Decimal("150.00"), "USD"))
    )
