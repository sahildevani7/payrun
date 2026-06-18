import pytest

from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner
from payrun.storage.unit_of_work import UnitOfWork


@pytest.fixture
def connection():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield conn
    conn.close()


def test_clean_exit_commits(connection):
    with UnitOfWork(connection) as conn:
        conn.execute(
            "INSERT INTO employees VALUES "
            "('E1','A','B','WEEKLY','2020-01-01','ACTIVE',NULL,'HOURLY','10.00','USD')"
        )
    rows = connection.execute("SELECT id FROM employees").fetchall()
    assert [row["id"] for row in rows] == ["E1"]


def test_exception_rolls_back(connection):
    with pytest.raises(ValueError):
        with UnitOfWork(connection) as conn:
            conn.execute(
                "INSERT INTO employees VALUES "
                "('E1','A','B','WEEKLY','2020-01-01','ACTIVE',NULL,'HOURLY','10.00','USD')"
            )
            raise ValueError("boom")
    rows = connection.execute("SELECT id FROM employees").fetchall()
    assert rows == []


def test_returns_the_wrapped_connection():
    conn = connect(":memory:")
    try:
        with UnitOfWork(conn) as inner:
            assert inner is conn
    finally:
        conn.close()
