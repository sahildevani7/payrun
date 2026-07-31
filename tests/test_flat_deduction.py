from decimal import Decimal

import pytest

from payrun.deductions.code import DeductionCode
from payrun.deductions.flat import FlatDeductionCalculator
from payrun.errors import CurrencyMismatchError
from payrun.money import Money


def test_flat_deduction_ignores_gross_amount():
    calculator = FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
    small = calculator.calculate(Money(Decimal("100.00"), "USD"))
    large = calculator.calculate(Money(Decimal("10000.00"), "USD"))
    assert small.amount == Money(Decimal("25.00"), "USD")
    assert large.amount == Money(Decimal("25.00"), "USD")


def test_flat_deduction_rejects_currency_mismatch():
    calculator = FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
    with pytest.raises(CurrencyMismatchError):
        calculator.calculate(Money(Decimal("100.00"), "CAD"))


def test_flat_deduction_carries_its_code():
    calculator = FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
    assert calculator.code == DeductionCode("PARKING")
    assert calculator.calculate(Money(Decimal("100.00"), "USD")).code == DeductionCode("PARKING")


def test_flat_deduction_of_zero_gross():
    calculator = FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
    assert calculator.calculate(Money.zero("USD")).amount == Money(Decimal("25.00"), "USD")
