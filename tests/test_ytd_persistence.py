from decimal import Decimal

import pytest

from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.run.ytd import YtdStore
from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner
from payrun.storage.repositories import load_ytd_store, save_ytd_store


@pytest.fixture
def connection():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield conn
    conn.close()


def test_load_from_empty_database_is_an_empty_store(connection):
    store = load_ytd_store(connection, "USD")
    assert store.items() == []


def test_save_then_load_round_trips_accumulators(connection):
    store = YtdStore("USD")
    store.record(
        EmployeeId("E0001"),
        gross=Money(Decimal("6500.00"), "USD"),
        pension=Money(Decimal("326.38"), "USD"),
        insurance=Money(Decimal("113.75"), "USD"),
        tax=Money(Decimal("961.67"), "USD"),
    )
    save_ytd_store(connection, store)

    reloaded = load_ytd_store(connection, "USD")
    accumulator = reloaded.get(EmployeeId("E0001"))
    assert accumulator.gross == Money(Decimal("6500.00"), "USD")
    assert accumulator.pension == Money(Decimal("326.38"), "USD")
    assert accumulator.insurance == Money(Decimal("113.75"), "USD")
    assert accumulator.tax == Money(Decimal("961.67"), "USD")


def test_save_overwrites_a_previously_saved_accumulator(connection):
    store = YtdStore("USD")
    store.record(
        EmployeeId("E0001"),
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money.zero("USD"),
        insurance=Money.zero("USD"),
        tax=Money.zero("USD"),
    )
    save_ytd_store(connection, store)

    store.record(
        EmployeeId("E0001"),
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money.zero("USD"),
        insurance=Money.zero("USD"),
        tax=Money.zero("USD"),
    )
    save_ytd_store(connection, store)

    reloaded = load_ytd_store(connection, "USD")
    assert reloaded.get(EmployeeId("E0001")).gross == Money(Decimal("2000.00"), "USD")
