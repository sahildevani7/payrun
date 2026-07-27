import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.period import PayPeriod
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.importers.base import TimesheetEntry
from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner
from payrun.storage.repositories import SqliteTimesheetRepository


@pytest.fixture
def repository():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield SqliteTimesheetRepository(conn)
    conn.close()


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )


def test_hours_for_period_sums_entries_within_range(repository):
    repository.add_entries(
        [
            TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 2), Hours(Decimal("8.00"))),
            TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 3), Hours(Decimal("7.50"))),
        ]
    )
    totals = repository.hours_for_period(_period())
    assert totals == {EmployeeId("E0001"): Hours(Decimal("15.50"))}


def test_hours_for_period_excludes_entries_outside_range(repository):
    repository.add_entries(
        [TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 4, 1), Hours(Decimal("8.00")))]
    )
    assert repository.hours_for_period(_period()) == {}


def test_add_entries_replaces_an_existing_entry_for_the_same_day(repository):
    repository.add_entries(
        [TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 2), Hours(Decimal("8.00")))]
    )
    repository.add_entries(
        [TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 2), Hours(Decimal("4.00")))]
    )
    totals = repository.hours_for_period(_period())
    assert totals == {EmployeeId("E0001"): Hours(Decimal("4.00"))}


def test_hours_for_period_with_no_entries_is_empty(repository):
    assert repository.hours_for_period(_period()) == {}
