from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.money import Money
from payrun.rate import Rate
from payrun.statutory.pension import PensionCalculator, annual_max_contribution
from payrun.statutory.tables import PensionParameters


def _params() -> PensionParameters:
    return PensionParameters(
        rate=Rate(Decimal("0.05")),
        exemption_annual=Money(Decimal("2600.00"), "USD"),
        ceiling_annual=Money(Decimal("62600.00"), "USD"),
    )


def test_annual_max_contribution_is_rate_times_taxable_band():
    assert annual_max_contribution(_params()) == Money(Decimal("3000.00"), "USD")


def test_contribution_is_rate_over_the_period_exemption():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("5000.00"), "USD"), ytd_contribution=Money.zero("USD")
    )
    # period exemption = 2600 / 12 = 216.67 (rounded), pensionable = 4783.33
    assert contribution == Money(Decimal("239.17"), "USD")


def test_gross_below_period_exemption_contributes_nothing():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("100.00"), "USD"), ytd_contribution=Money.zero("USD")
    )
    assert contribution == Money.zero("USD")


def test_contribution_is_capped_at_remaining_annual_room():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("5000.00"), "USD"),
        ytd_contribution=Money(Decimal("2900.00"), "USD"),
    )
    assert contribution == Money(Decimal("100.00"), "USD")


def test_contribution_is_zero_once_annual_maximum_is_reached():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("5000.00"), "USD"),
        ytd_contribution=Money(Decimal("3000.00"), "USD"),
    )
    assert contribution == Money.zero("USD")


def test_running_total_never_exceeds_the_annual_maximum():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    ytd = Money.zero("USD")
    for _ in range(12):
        contribution = calculator.calculate(
            gross=Money(Decimal("5000.00"), "USD"), ytd_contribution=ytd
        )
        ytd = ytd + contribution
    assert ytd <= annual_max_contribution(_params())


def test_gross_exactly_at_period_exemption_contributes_nothing():
    calculator = PensionCalculator(_params(), Frequency.MONTHLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("216.67"), "USD"), ytd_contribution=Money.zero("USD")
    )
    assert contribution == Money.zero("USD")


def test_weekly_frequency_uses_a_smaller_period_exemption():
    calculator = PensionCalculator(_params(), Frequency.WEEKLY)
    contribution = calculator.calculate(
        gross=Money(Decimal("1000.00"), "USD"), ytd_contribution=Money.zero("USD")
    )
    assert contribution > Money.zero("USD")
