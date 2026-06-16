import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.errors import NotFoundError, ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.people.repository import EmployeeRepository, InMemoryEmployeeRepository


def _employee(employee_id: str) -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )


def test_in_memory_repository_satisfies_the_protocol():
    assert isinstance(InMemoryEmployeeRepository(), EmployeeRepository)


def test_add_then_get_returns_the_same_employee():
    repo = InMemoryEmployeeRepository()
    employee = _employee("E0007")
    repo.add(employee)
    assert repo.get(EmployeeId("E0007")) == employee


def test_get_missing_employee_raises_not_found():
    repo = InMemoryEmployeeRepository()
    with pytest.raises(NotFoundError):
        repo.get(EmployeeId("E9999"))


def test_add_duplicate_id_raises_validation_error():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0007"))
    with pytest.raises(ValidationError):
        repo.add(_employee("E0007"))


def test_list_all_returns_employees_sorted_by_id():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0009"))
    repo.add(_employee("E0001"))
    repo.add(_employee("E0005"))
    assert [str(e.id) for e in repo.list_all()] == ["E0001", "E0005", "E0009"]


def test_list_all_on_empty_repository_returns_empty_list():
    assert InMemoryEmployeeRepository().list_all() == []
