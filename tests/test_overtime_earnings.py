import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.earnings.overtime import OvertimeEarningCalculator, default_calculator
from payrun.errors import ValidationError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.rate import Rate


def _hourly_employee(hourly_rate: str) -> Employee:
    return Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.WEEKLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal(hourly_rate), "USD")),
    )


def test_no_overtime_below_threshold():
    line = default_calculator().calculate(_hourly_employee("20.00"), Hours(Decimal("35")))
    assert line.amount == Money.zero("USD")
    assert line.hours == Hours.zero()


def test_overtime_pays_multiplier_on_hours_above_threshold():
    line = default_calculator().calculate(_hourly_employee("20.00"), Hours(Decimal("45")))
    assert line.hours == Hours(Decimal("5"))
    assert line.amount == Money(Decimal("150.00"), "USD")


def test_default_calculator_exposes_its_weekly_threshold():
    assert default_calculator().weekly_threshold == Hours(Decimal("40"))


def test_exactly_at_threshold_has_no_overtime():
    line = default_calculator().calculate(_hourly_employee("20.00"), Hours(Decimal("40")))
    assert line.amount == Money.zero("USD")


def test_custom_threshold_and_multiplier():
    calculator = OvertimeEarningCalculator(
        weekly_threshold=Hours(Decimal("35")), multiplier=Rate(Decimal("2"))
    )
    line = calculator.calculate(_hourly_employee("10.00"), Hours(Decimal("40")))
    assert line.hours == Hours(Decimal("5"))
    assert line.amount == Money(Decimal("100.00"), "USD")


def test_rejects_salaried_employees():
    employee = Employee(
        id=EmployeeId("E0008"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.WEEKLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("60000.00"), "USD")),
    )
    with pytest.raises(ValidationError):
        default_calculator().calculate(employee, Hours(Decimal("45")))
