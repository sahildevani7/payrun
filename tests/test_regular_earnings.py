import datetime as dt
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.earnings.regular import RegularEarningCalculator
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus


def _employee(frequency: Frequency, compensation) -> Employee:
    return Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=frequency,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=compensation,
    )


def test_hourly_pay_multiplies_rate_by_hours():
    employee = _employee(
        Frequency.WEEKLY, HourlyCompensation(Money(Decimal("32.50"), "USD"))
    )
    line = RegularEarningCalculator().calculate(employee, Hours(Decimal("40")))
    assert line.amount == Money(Decimal("1300.00"), "USD")
    assert line.hours == Hours(Decimal("40"))


def test_hourly_pay_rounds_half_up_to_the_cent():
    employee = _employee(
        Frequency.WEEKLY, HourlyCompensation(Money(Decimal("32.335"), "USD"))
    )
    line = RegularEarningCalculator().calculate(employee, Hours(Decimal("0.25")))
    assert line.amount == Money(Decimal("8.08"), "USD")


def test_salaried_pay_is_annual_amount_divided_by_periods_per_year():
    employee = _employee(
        Frequency.MONTHLY, SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    )
    line = RegularEarningCalculator().calculate(employee, Hours.zero())
    assert line.amount == Money(Decimal("6500.00"), "USD")
    assert line.hours is None


def test_salaried_pay_rounds_when_annual_amount_does_not_divide_evenly():
    employee = _employee(
        Frequency.BIWEEKLY, SalariedCompensation(Money(Decimal("50000.00"), "USD"))
    )
    line = RegularEarningCalculator().calculate(employee, Hours.zero())
    assert line.amount == Money(Decimal("1923.08"), "USD")


def test_salaried_pay_ignores_hours_argument():
    employee = _employee(
        Frequency.MONTHLY, SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    )
    with_zero_hours = RegularEarningCalculator().calculate(employee, Hours.zero())
    with_some_hours = RegularEarningCalculator().calculate(employee, Hours(Decimal("10")))
    assert with_zero_hours.amount == with_some_hours.amount
