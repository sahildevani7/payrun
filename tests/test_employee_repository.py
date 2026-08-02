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


def _employee(
    employee_id: str,
    frequency: Frequency = Frequency.BIWEEKLY,
    employment: Employment | None = None,
) -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Jordan",
        last_name="Lee",
        frequency=frequency,
        employment=employment
        or Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
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


def test_get_does_not_mutate_the_repository():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0007"))
    repo.get(EmployeeId("E0007"))
    assert len(repo.list_all()) == 1


def test_repository_holds_multiple_distinct_employees():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0001"))
    repo.add(_employee("E0002"))
    assert repo.get(EmployeeId("E0001")).id != repo.get(EmployeeId("E0002")).id


def test_list_by_frequency_filters_to_the_matching_frequency():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0001", frequency=Frequency.WEEKLY))
    repo.add(_employee("E0002", frequency=Frequency.MONTHLY))
    assert [str(e.id) for e in repo.list_by_frequency(Frequency.WEEKLY)] == ["E0001"]


def test_list_by_frequency_with_no_matches_is_empty():
    repo = InMemoryEmployeeRepository()
    repo.add(_employee("E0001", frequency=Frequency.WEEKLY))
    assert repo.list_by_frequency(Frequency.MONTHLY) == []


def test_list_active_on_excludes_employees_not_yet_hired():
    repo = InMemoryEmployeeRepository()
    repo.add(
        _employee(
            "E0001",
            employment=Employment(hire_date=dt.date(2026, 6, 1), status=EmploymentStatus.ACTIVE),
        )
    )
    assert repo.list_active_on(dt.date(2026, 1, 1)) == []
    assert len(repo.list_active_on(dt.date(2026, 6, 1))) == 1


def test_list_active_on_excludes_terminated_employees():
    repo = InMemoryEmployeeRepository()
    repo.add(
        _employee(
            "E0001",
            employment=Employment(
                hire_date=dt.date(2020, 1, 1),
                status=EmploymentStatus.TERMINATED,
                termination_date=dt.date(2026, 1, 15),
            ),
        )
    )
    assert repo.list_active_on(dt.date(2026, 1, 15)) != []
    assert repo.list_active_on(dt.date(2026, 1, 16)) == []
