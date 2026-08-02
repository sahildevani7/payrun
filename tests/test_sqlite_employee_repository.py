import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.errors import NotFoundError, ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner
from payrun.storage.repositories import SqliteEmployeeRepository


@pytest.fixture
def repository():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield SqliteEmployeeRepository(conn)
    conn.close()


def _salaried_employee(employee_id: str) -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.BIWEEKLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )


def test_add_then_get_round_trips_a_salaried_employee(repository):
    employee = _salaried_employee("E0007")
    repository.add(employee)
    assert repository.get(EmployeeId("E0007")) == employee


def test_add_then_get_round_trips_an_hourly_employee(repository):
    employee = Employee(
        id=EmployeeId("E0008"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.WEEKLY,
        employment=Employment(hire_date=dt.date(2021, 6, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
    )
    repository.add(employee)
    round_tripped = repository.get(EmployeeId("E0008"))
    assert isinstance(round_tripped.compensation, HourlyCompensation)
    assert round_tripped.compensation.hourly_rate == Money(Decimal("32.50"), "USD")


def test_round_trips_a_terminated_employment(repository):
    employee = Employee(
        id=EmployeeId("E0009"),
        first_name="Sam",
        last_name="Rivera",
        frequency=Frequency.MONTHLY,
        employment=Employment(
            hire_date=dt.date(2019, 3, 1),
            status=EmploymentStatus.TERMINATED,
            termination_date=dt.date(2026, 2, 28),
        ),
        compensation=SalariedCompensation(Money(Decimal("60000.00"), "USD")),
    )
    repository.add(employee)
    round_tripped = repository.get(EmployeeId("E0009"))
    assert round_tripped.employment.termination_date == dt.date(2026, 2, 28)


def test_get_missing_employee_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get(EmployeeId("E9999"))


def test_add_duplicate_id_raises_validation_error(repository):
    repository.add(_salaried_employee("E0007"))
    with pytest.raises(ValidationError):
        repository.add(_salaried_employee("E0007"))


def test_list_all_returns_employees_sorted_by_id(repository):
    repository.add(_salaried_employee("E0009"))
    repository.add(_salaried_employee("E0001"))
    repository.add(_salaried_employee("E0005"))
    assert [str(e.id) for e in repository.list_all()] == ["E0001", "E0005", "E0009"]


def test_round_trips_an_active_employment_with_no_termination_date(repository):
    employee = _salaried_employee("E0007")
    repository.add(employee)
    round_tripped = repository.get(EmployeeId("E0007"))
    assert round_tripped.employment.termination_date is None
    assert round_tripped.employment.status.value == "ACTIVE"


def test_round_trip_preserves_frequency(repository):
    employee = Employee(
        id=EmployeeId("E0010"),
        first_name="Priya",
        last_name="Nair",
        frequency=Frequency.WEEKLY,
        employment=Employment(hire_date=dt.date(2022, 5, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("52000.00"), "USD")),
    )
    repository.add(employee)
    assert repository.get(EmployeeId("E0010")).frequency == Frequency.WEEKLY


def test_list_by_frequency_filters_to_the_matching_frequency(repository):
    repository.add(_salaried_employee("E0001"))
    repository.add(
        Employee(
            id=EmployeeId("E0002"),
            first_name="Ada",
            last_name="Okafor",
            frequency=Frequency.WEEKLY,
            employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
            compensation=HourlyCompensation(Money(Decimal("32.50"), "USD")),
        )
    )
    assert [str(e.id) for e in repository.list_by_frequency(Frequency.BIWEEKLY)] == ["E0001"]


def test_list_active_on_excludes_employees_not_yet_hired(repository):
    repository.add(
        Employee(
            id=EmployeeId("E0001"),
            first_name="Jordan",
            last_name="Lee",
            frequency=Frequency.MONTHLY,
            employment=Employment(hire_date=dt.date(2026, 6, 1), status=EmploymentStatus.ACTIVE),
            compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
        )
    )
    assert repository.list_active_on(dt.date(2026, 1, 1)) == []
    assert len(repository.list_active_on(dt.date(2026, 6, 1))) == 1


def test_list_active_on_excludes_terminated_employees(repository):
    repository.add(
        Employee(
            id=EmployeeId("E0001"),
            first_name="Jordan",
            last_name="Lee",
            frequency=Frequency.MONTHLY,
            employment=Employment(
                hire_date=dt.date(2020, 1, 1),
                status=EmploymentStatus.TERMINATED,
                termination_date=dt.date(2026, 1, 15),
            ),
            compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
        )
    )
    assert len(repository.list_active_on(dt.date(2026, 1, 15))) == 1
    assert repository.list_active_on(dt.date(2026, 1, 16)) == []
