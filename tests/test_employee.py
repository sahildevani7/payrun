import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.errors import ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus


def _employment() -> Employment:
    return Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE)


def test_full_name_joins_first_and_last():
    employee = Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=_employment(),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    assert employee.full_name == "Jordan Lee"


def test_rejects_blank_first_name():
    with pytest.raises(ValidationError):
        Employee(
            id=EmployeeId("E0007"),
            first_name="   ",
            last_name="Lee",
            frequency=Frequency.BIWEEKLY,
            employment=_employment(),
            compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
        )


def test_rejects_blank_last_name():
    with pytest.raises(ValidationError):
        Employee(
            id=EmployeeId("E0007"),
            first_name="Jordan",
            last_name="",
            frequency=Frequency.BIWEEKLY,
            employment=_employment(),
            compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
        )


def test_accepts_hourly_compensation():
    employee = Employee(
        id=EmployeeId("E0008"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.WEEKLY,
        employment=_employment(),
        compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
    )
    assert isinstance(employee.compensation, HourlyCompensation)


def test_employee_is_frozen():
    employee = Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=_employment(),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    with pytest.raises(AttributeError):
        employee.first_name = "Sam"  # type: ignore[misc]


def test_full_name_strips_no_internal_whitespace():
    employee = Employee(
        id=EmployeeId("E0007"),
        first_name="Mary Jane",
        last_name="Watson",
        frequency=Frequency.BIWEEKLY,
        employment=_employment(),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    assert employee.full_name == "Mary Jane Watson"


def test_equal_employees_are_equal():
    employee_a = Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=_employment(),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    employee_b = Employee(
        id=EmployeeId("E0007"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=_employment(),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )
    assert employee_a == employee_b
