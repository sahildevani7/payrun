from decimal import Decimal

from payrun.money import Money
from payrun.tax.credits import apply_credit


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
