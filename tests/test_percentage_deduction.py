from decimal import Decimal

from payrun.deductions.code import DeductionCode
from payrun.deductions.percentage import PercentageDeductionCalculator
from payrun.money import Money
from payrun.rate import Rate


def test_percentage_deduction_scales_with_gross():
    calculator = PercentageDeductionCalculator(DeductionCode("UNION"), Rate(Decimal("0.02")))
    line = calculator.calculate(Money(Decimal("2000.00"), "USD"))
    assert line.amount == Money(Decimal("40.00"), "USD")


def test_percentage_deduction_rounds_half_up_to_the_cent():
    calculator = PercentageDeductionCalculator(DeductionCode("UNION"), Rate(Decimal("0.015")))
    line = calculator.calculate(Money(Decimal("100.03"), "USD"))
    assert line.amount == Money(Decimal("1.50"), "USD")


def test_zero_rate_produces_zero_deduction():
    calculator = PercentageDeductionCalculator(DeductionCode("UNION"), Rate.zero())
    line = calculator.calculate(Money(Decimal("2000.00"), "USD"))
    assert line.amount == Money.zero("USD")


def test_percentage_deduction_of_zero_gross_is_zero():
    calculator = PercentageDeductionCalculator(DeductionCode("UNION"), Rate(Decimal("0.02")))
    line = calculator.calculate(Money.zero("USD"))
    assert line.amount == Money.zero("USD")


def test_percentage_deduction_preserves_currency():
    calculator = PercentageDeductionCalculator(DeductionCode("UNION"), Rate(Decimal("0.02")))
    line = calculator.calculate(Money(Decimal("2000.00"), "CAD"))
    assert line.amount.currency == "CAD"
