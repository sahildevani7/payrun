import sqlite3

from payrun.storage.engine import connect, connect_and_migrate


def test_connect_returns_a_connection_with_row_factory():
    connection = connect(":memory:")
    try:
        assert isinstance(connection, sqlite3.Connection)
        assert connection.row_factory is sqlite3.Row
    finally:
        connection.close()


def test_connect_enables_foreign_keys():
    connection = connect(":memory:")
    try:
        (value,) = connection.execute("PRAGMA foreign_keys").fetchone()
        assert value == 1
    finally:
        connection.close()


def test_connect_and_migrate_applies_all_migrations():
    connection = connect_and_migrate(":memory:")
    try:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert "employees" in tables
        assert "payslips" in tables
    finally:
        connection.close()


def test_connect_and_migrate_is_idempotent(tmp_path):
    path = str(tmp_path / "payrun.db")
    connect_and_migrate(path).close()
    connection = connect_and_migrate(path)
    try:
        row = connection.execute("SELECT COUNT(*) AS n FROM schema_migrations").fetchone()
        assert row["n"] == 3
    finally:
        connection.close()
