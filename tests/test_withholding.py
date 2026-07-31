from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.money import Money
from payrun.rate import Rate
from payrun.statutory.tables import TaxParameters
from payrun.tax.brackets import TaxBracket
from payrun.tax.withholding import WithholdingCalculator


def _params() -> TaxParameters:
    return TaxParameters(
        basic_credit_annual=Money(Decimal("600.00"), "USD"),
        brackets=(
            TaxBracket(Money(Decimal("0.00"), "USD"), Rate(Decimal("0.10"))),
            TaxBracket(Money(Decimal("12000.00"), "USD"), Rate(Decimal("0.20"))),
        ),
    )


def test_withholding_within_first_bracket():
    calculator = WithholdingCalculator(_params(), Frequency.MONTHLY)
    withheld = calculator.calculate(Money(Decimal("1000.00"), "USD"))
    assert withheld == Money(Decimal("50.00"), "USD")


def test_withholding_spanning_two_brackets():
    calculator = WithholdingCalculator(_params(), Frequency.MONTHLY)
    withheld = calculator.calculate(Money(Decimal("2000.00"), "USD"))
    assert withheld == Money(Decimal("250.00"), "USD")


def test_withholding_scales_with_frequency():
    monthly = WithholdingCalculator(_params(), Frequency.MONTHLY).calculate(
        Money(Decimal("1000.00"), "USD")
    )
    biweekly = WithholdingCalculator(_params(), Frequency.BIWEEKLY).calculate(
        Money(Decimal("1000.00"), "USD")
    )
    assert monthly != biweekly


def test_zero_gross_withholds_nothing():
    calculator = WithholdingCalculator(_params(), Frequency.MONTHLY)
    withheld = calculator.calculate(Money.zero("USD"))
    assert withheld == Money.zero("USD")


def test_low_income_within_credit_withholds_nothing():
    calculator = WithholdingCalculator(_params(), Frequency.MONTHLY)
    withheld = calculator.calculate(Money(Decimal("400.00"), "USD"))
    assert withheld == Money.zero("USD")


def test_weekly_withholding_is_smaller_than_monthly_for_the_same_gross():
    weekly = WithholdingCalculator(_params(), Frequency.WEEKLY).calculate(
        Money(Decimal("1000.00"), "USD")
    )
    monthly = WithholdingCalculator(_params(), Frequency.MONTHLY).calculate(
        Money(Decimal("1000.00"), "USD")
    )
    assert weekly > monthly
