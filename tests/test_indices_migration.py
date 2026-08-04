import pytest

from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner


@pytest.fixture
def connection():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield conn
    conn.close()


def _index_names(connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index'"
    ).fetchall()
    return {row["name"] for row in rows}


def test_creates_an_index_on_employee_frequency(connection):
    assert "idx_employees_frequency" in _index_names(connection)


def test_creates_indices_on_employment_dates(connection):
    indices = _index_names(connection)
    assert "idx_employees_hire_date" in indices
    assert "idx_employees_termination_date" in indices


def test_creates_an_index_on_timesheet_work_date(connection):
    assert "idx_timesheet_entries_work_date" in _index_names(connection)
