import sqlite3

from payrun.storage.engine import connect


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
