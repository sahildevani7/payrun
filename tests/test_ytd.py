from decimal import Decimal

import pytest

from payrun.errors import CurrencyMismatchError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.run.ytd import YtdAccumulator, YtdStore


def test_zero_accumulator_has_all_zero_buckets():
    accumulator = YtdAccumulator.zero("USD")
    assert accumulator.gross == Money.zero("USD")
    assert accumulator.pension == Money.zero("USD")
    assert accumulator.insurance == Money.zero("USD")
    assert accumulator.tax == Money.zero("USD")


def test_plus_adds_to_every_bucket():
    accumulator = YtdAccumulator.zero("USD").plus(
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money(Decimal("50.00"), "USD"),
        insurance=Money(Decimal("20.00"), "USD"),
        tax=Money(Decimal("100.00"), "USD"),
    )
    assert accumulator.gross == Money(Decimal("1000.00"), "USD")
    assert accumulator.pension == Money(Decimal("50.00"), "USD")
    assert accumulator.insurance == Money(Decimal("20.00"), "USD")
    assert accumulator.tax == Money(Decimal("100.00"), "USD")


def test_store_get_defaults_to_zero_for_unknown_employee():
    store = YtdStore("USD")
    assert store.get(EmployeeId("E0007")) == YtdAccumulator.zero("USD")


def test_store_record_accumulates_across_calls():
    store = YtdStore("USD")
    employee_id = EmployeeId("E0007")
    store.record(
        employee_id,
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money(Decimal("50.00"), "USD"),
        insurance=Money(Decimal("20.00"), "USD"),
        tax=Money(Decimal("100.00"), "USD"),
    )
    store.record(
        employee_id,
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money(Decimal("50.00"), "USD"),
        insurance=Money(Decimal("20.00"), "USD"),
        tax=Money(Decimal("100.00"), "USD"),
    )
    accumulator = store.get(employee_id)
    assert accumulator.gross == Money(Decimal("2000.00"), "USD")
    assert accumulator.pension == Money(Decimal("100.00"), "USD")


def test_store_rejects_currency_mismatch():
    store = YtdStore("USD")
    with pytest.raises(CurrencyMismatchError):
        store.record(
            EmployeeId("E0007"),
            gross=Money(Decimal("1000.00"), "CAD"),
            pension=Money.zero("CAD"),
            insurance=Money.zero("CAD"),
            tax=Money.zero("CAD"),
        )


def test_store_tracks_employees_independently():
    store = YtdStore("USD")
    store.record(
        EmployeeId("E0001"),
        gross=Money(Decimal("1000.00"), "USD"),
        pension=Money.zero("USD"),
        insurance=Money.zero("USD"),
        tax=Money.zero("USD"),
    )
    assert store.get(EmployeeId("E0002")) == YtdAccumulator.zero("USD")
