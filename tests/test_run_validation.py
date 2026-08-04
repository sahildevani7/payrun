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


def test_accepts_multiple_distinct_active_employees():
    employees = [
        _salaried("E0001", dt.date(2020, 1, 1)),
        _salaried("E0002", dt.date(2020, 1, 1)),
    ]
    validate_run(employees, _period(), {})


def test_employee_terminated_exactly_on_period_end_is_active():
    employee = Employee(
        id=EmployeeId("E0001"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.SEMIMONTHLY,
        employment=Employment(
            hire_date=dt.date(2020, 1, 1),
            status=EmploymentStatus.TERMINATED,
            termination_date=dt.date(2026, 3, 15),
        ),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    validate_run([employee], _period(), {})


def test_accepts_employee_currency_matching_the_run_currency():
    employee = _salaried("E0001", dt.date(2020, 1, 1))
    validate_run([employee], _period(), {}, currency="USD")


def test_rejects_employee_currency_not_matching_the_run_currency():
    employee = _salaried("E0001", dt.date(2020, 1, 1))
    with pytest.raises(RunError):
        validate_run([employee], _period(), {}, currency="CAD")


def test_currency_check_is_skipped_when_not_provided():
    employee = _salaried("E0001", dt.date(2020, 1, 1))
    validate_run([employee], _period(), {})


def test_rejects_hourly_employee_currency_not_matching_the_run_currency():
    employee = Employee(
        id=EmployeeId("E0002"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.SEMIMONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
    )
    hours = {EmployeeId("E0002"): Hours(Decimal("80"))}
    with pytest.raises(RunError):
        validate_run([employee], _period(), hours, currency="CAD")
