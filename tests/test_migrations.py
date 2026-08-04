import sqlite3

import pytest

from payrun.errors import MigrationError
from payrun.storage.engine import connect
from payrun.storage.migrations.runner import Migration, MigrationRunner


@pytest.fixture
def connection():
    conn = connect(":memory:")
    yield conn
    conn.close()


def test_run_applies_all_migrations_and_creates_employees_table(connection):
    applied = MigrationRunner().run(connection)
    assert "0001_create_employees" in applied
    assert "0002_create_run_tables" in applied
    assert "0003_add_indices" in applied
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    assert "employees" in tables
    assert "schema_migrations" in tables
    assert "timesheet_entries" in tables
    assert "payslips" in tables
    assert "ytd_accumulators" in tables


def test_run_is_idempotent(connection):
    runner = MigrationRunner()
    first = runner.run(connection)
    second = runner.run(connection)
    assert first
    assert second == []


def test_applied_lists_migration_names_in_order(connection):
    runner = MigrationRunner()
    runner.run(connection)
    assert runner.applied(connection) == [
        "0001_create_employees",
        "0002_create_run_tables",
        "0003_add_indices",
    ]


def test_duplicate_migration_names_are_rejected():
    def noop(conn: sqlite3.Connection) -> None:
        pass

    with pytest.raises(MigrationError):
        MigrationRunner([Migration("dup", noop), Migration("dup", noop)])


def test_failing_migration_raises_and_leaves_schema_migrations_untouched(connection):
    def broken(conn: sqlite3.Connection) -> None:
        conn.execute("CREATE TABLE this is not valid sql")

    runner = MigrationRunner([Migration("broken", broken)])
    with pytest.raises(MigrationError):
        runner.run(connection)
    assert runner.applied(connection) == []


def test_applied_on_a_fresh_connection_is_empty(connection):
    assert MigrationRunner().applied(connection) == []


def test_run_with_no_migrations_configured_applies_nothing(connection):
    assert MigrationRunner([]).run(connection) == []


def test_default_migrations_list_matches_module_migrations():
    from payrun.storage.migrations.runner import MIGRATIONS

    assert [m.name for m in MIGRATIONS] == [
        "0001_create_employees",
        "0002_create_run_tables",
        "0003_add_indices",
    ]
