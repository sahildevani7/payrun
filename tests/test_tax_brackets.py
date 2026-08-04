from decimal import Decimal

import pytest

from payrun.errors import ValidationError
from payrun.money import Money
from payrun.rate import Rate
from payrun.tax.brackets import TaxBracket, compute_tax, validate_ascending


def _brackets() -> list[TaxBracket]:
    return [
        TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10"))),
        TaxBracket(Money(Decimal("10000.00"), "USD"), Rate(Decimal("0.20"))),
        TaxBracket(Money(Decimal("40000.00"), "USD"), Rate(Decimal("0.30"))),
    ]


def test_income_within_first_bracket_is_taxed_at_its_rate():
    tax = compute_tax(Money(Decimal("5000.00"), "USD"), _brackets())
    assert tax == Money(Decimal("500.00"), "USD")


def test_income_spanning_two_brackets_sums_the_slices():
    # 10000 * 0.10 + 5000 * 0.20 = 1000 + 1000 = 2000
    tax = compute_tax(Money(Decimal("15000.00"), "USD"), _brackets())
    assert tax == Money(Decimal("2000.00"), "USD")


def test_income_spanning_all_brackets_sums_every_slice():
    # 10000*0.10 + 30000*0.20 + 10000*0.30 = 1000 + 6000 + 3000 = 10000
    tax = compute_tax(Money(Decimal("50000.00"), "USD"), _brackets())
    assert tax == Money(Decimal("10000.00"), "USD")


def test_zero_income_produces_zero_tax():
    tax = compute_tax(Money.zero("USD"), _brackets())
    assert tax == Money.zero("USD")


def test_income_exactly_at_a_threshold_does_not_enter_that_bracket():
    tax = compute_tax(Money(Decimal("10000.00"), "USD"), _brackets())
    assert tax == Money(Decimal("1000.00"), "USD")


def test_rejects_empty_bracket_table():
    with pytest.raises(ValidationError):
        compute_tax(Money(Decimal("100.00"), "USD"), [])


def test_rejects_bracket_currency_mismatch():
    mismatched = [TaxBracket(Money(Decimal("0.00"), "CAD"), Rate(Decimal("0.10")))]
    with pytest.raises(ValidationError):
        compute_tax(Money(Decimal("100.00"), "USD"), mismatched)


def test_single_bracket_table_taxes_everything_at_one_rate():
    brackets = [TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.15")))]
    tax = compute_tax(Money(Decimal("1000.00"), "USD"), brackets)
    assert tax == Money(Decimal("150.00"), "USD")


def test_income_just_below_a_threshold_stays_in_the_lower_bracket():
    tax = compute_tax(Money(Decimal("9999.99"), "USD"), _brackets())
    assert tax == Money(Decimal("1000.00"), "USD")


def test_validate_ascending_accepts_a_well_formed_table():
    validate_ascending(_brackets())


def test_validate_ascending_rejects_empty_table():
    with pytest.raises(ValidationError):
        validate_ascending([])


def test_validate_ascending_rejects_nonzero_first_threshold():
    brackets = [TaxBracket(Money(Decimal("100.00"), "USD"), Rate(Decimal("0.10")))]
    with pytest.raises(ValidationError):
        validate_ascending(brackets)


def test_validate_ascending_rejects_out_of_order_thresholds():
    brackets = [
        TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10"))),
        TaxBracket(Money(Decimal("5000.00"), "USD"), Rate(Decimal("0.20"))),
        TaxBracket(Money(Decimal("2000.00"), "USD"), Rate(Decimal("0.30"))),
    ]
    with pytest.raises(ValidationError):
        validate_ascending(brackets)


def test_validate_ascending_rejects_duplicate_thresholds():
    brackets = [
        TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10"))),
        TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.20"))),
    ]
    with pytest.raises(ValidationError):
        validate_ascending(brackets)


def test_validate_ascending_rejects_mixed_currencies():
    brackets = [
        TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10"))),
        TaxBracket(Money(Decimal("5000.00"), "CAD"), Rate(Decimal("0.20"))),
    ]
    with pytest.raises(ValidationError):
        validate_ascending(brackets)


def test_validate_ascending_accepts_a_single_bracket():
    validate_ascending([TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10")))])
