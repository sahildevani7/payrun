import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.period import PayPeriod
from payrun.errors import RunError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.run.validation import validate_run


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )


def _salaried(employee_id: str, hire_date: dt.date) -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.SEMIMONTHLY,
        employment=Employment(hire_date=hire_date, status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )


def test_rejects_empty_employee_list():
    with pytest.raises(RunError):
        validate_run([], _period(), {})


def test_accepts_active_salaried_employee_with_no_hours_required():
    validate_run([_salaried("E0001", dt.date(2020, 1, 1))], _period(), {})


def test_rejects_employee_hired_after_the_period():
    employee = _salaried("E0001", dt.date(2026, 4, 1))
    with pytest.raises(RunError):
        validate_run([employee], _period(), {})


def test_rejects_duplicate_employee_ids():
    employee = _salaried("E0001", dt.date(2020, 1, 1))
    with pytest.raises(RunError):
        validate_run([employee, employee], _period(), {})


def test_rejects_hourly_employee_missing_timesheet_hours():
    employee = Employee(
        id=EmployeeId("E0002"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.SEMIMONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
    )
    with pytest.raises(RunError):
        validate_run([employee], _period(), {})


def test_accepts_hourly_employee_with_timesheet_hours():
    employee = Employee(
        id=EmployeeId("E0002"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.SEMIMONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
    )
    validate_run([employee], _period(), {EmployeeId("E0002"): Hours(Decimal("80"))})
