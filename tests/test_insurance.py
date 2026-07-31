from decimal import Decimal

from payrun.money import Money
from payrun.rate import Rate
from payrun.statutory.insurance import InsuranceCalculator
from payrun.statutory.tables import InsuranceParameters


def _params() -> InsuranceParameters:
    return InsuranceParameters(
        rate=Rate(Decimal("0.02")), annual_maximum=Money(Decimal("500.00"), "USD")
    )


def test_premium_is_rate_times_gross():
    calculator = InsuranceCalculator(_params())
    premium = calculator.calculate(
        gross=Money(Decimal("2000.00"), "USD"), ytd_premium=Money.zero("USD")
    )
    assert premium == Money(Decimal("40.00"), "USD")


def test_premium_is_capped_at_remaining_annual_room():
    calculator = InsuranceCalculator(_params())
    premium = calculator.calculate(
        gross=Money(Decimal("2000.00"), "USD"), ytd_premium=Money(Decimal("470.00"), "USD")
    )
    assert premium == Money(Decimal("30.00"), "USD")


def test_premium_is_zero_once_annual_maximum_reached():
    calculator = InsuranceCalculator(_params())
    premium = calculator.calculate(
        gross=Money(Decimal("2000.00"), "USD"), ytd_premium=Money(Decimal("500.00"), "USD")
    )
    assert premium == Money.zero("USD")


def test_zero_gross_produces_zero_premium():
    calculator = InsuranceCalculator(_params())
    premium = calculator.calculate(gross=Money.zero("USD"), ytd_premium=Money.zero("USD"))
    assert premium == Money.zero("USD")


def test_premium_exceeding_ytd_room_by_a_cent_is_capped():
    calculator = InsuranceCalculator(_params())
    premium = calculator.calculate(
        gross=Money(Decimal("2000.00"), "USD"), ytd_premium=Money(Decimal("499.99"), "USD")
    )
    assert premium == Money(Decimal("0.01"), "USD")


def test_running_total_never_exceeds_the_annual_maximum():
    calculator = InsuranceCalculator(_params())
    ytd = Money.zero("USD")
    for _ in range(30):
        premium = calculator.calculate(gross=Money(Decimal("2000.00"), "USD"), ytd_premium=ytd)
        ytd = ytd + premium
    assert ytd <= _params().annual_maximum
