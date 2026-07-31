import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.run.result import PayRunResult, PaySlip
from payrun.storage.engine import connect
from payrun.storage.migrations.runner import MigrationRunner
from payrun.storage.repositories import SqlitePayRunRepository


@pytest.fixture
def repository():
    conn = connect(":memory:")
    MigrationRunner().run(conn)
    yield SqlitePayRunRepository(conn)
    conn.close()


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )


def _payslip(employee_id: str) -> PaySlip:
    return PaySlip(
        employee_id=EmployeeId(employee_id),
        period=_period(),
        earnings=(
            EarningLine(
                EarningCode("REGULAR"),
                Money(Decimal("1300.00"), "USD"),
                hours=Hours(Decimal("40")),
            ),
        ),
        deductions=(DeductionLine(DeductionCode("TAX"), Money(Decimal("130.00"), "USD")),),
        employer_contributions=(
            DeductionLine(DeductionCode("PENSION"), Money(Decimal("65.00"), "USD")),
        ),
        gross=Money(Decimal("1300.00"), "USD"),
        net=Money(Decimal("1170.00"), "USD"),
    )


def test_get_payslip_round_trips_a_saved_payslip(repository):
    result = PayRunResult(period=_period(), payslips=(_payslip("E0001"),))
    repository.save(result)
    round_tripped = repository.get_payslip(EmployeeId("E0001"), _period().start)
    assert round_tripped == _payslip("E0001")


def test_get_payslip_missing_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get_payslip(EmployeeId("E9999"), _period().start)


def test_get_register_returns_all_payslips_for_the_period(repository):
    result = PayRunResult(
        period=_period(), payslips=(_payslip("E0002"), _payslip("E0001"))
    )
    repository.save(result)
    register = repository.get_register(_period().start)
    assert [str(p.employee_id) for p in register.payslips] == ["E0001", "E0002"]
    assert register.period == _period()


def test_get_register_missing_period_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get_register(dt.date(2099, 1, 1))


def test_save_overwrites_a_previously_saved_payslip(repository):
    repository.save(PayRunResult(period=_period(), payslips=(_payslip("E0001"),)))
    updated = PaySlip(
        employee_id=EmployeeId("E0001"),
        period=_period(),
        earnings=_payslip("E0001").earnings,
        deductions=_payslip("E0001").deductions,
        employer_contributions=(),
        gross=Money(Decimal("1300.00"), "USD"),
        net=Money(Decimal("1200.00"), "USD"),
    )
    repository.save(PayRunResult(period=_period(), payslips=(updated,)))
    round_tripped = repository.get_payslip(EmployeeId("E0001"), _period().start)
    assert round_tripped.net == Money(Decimal("1200.00"), "USD")


def test_round_trip_preserves_earning_hours(repository):
    result = PayRunResult(period=_period(), payslips=(_payslip("E0001"),))
    repository.save(result)
    round_tripped = repository.get_payslip(EmployeeId("E0001"), _period().start)
    assert round_tripped.earnings[0].hours == Hours(Decimal("40"))


def test_round_trip_preserves_employer_contributions(repository):
    result = PayRunResult(period=_period(), payslips=(_payslip("E0001"),))
    repository.save(result)
    round_tripped = repository.get_payslip(EmployeeId("E0001"), _period().start)
    assert round_tripped.employer_contributions == _payslip("E0001").employer_contributions


def test_get_register_on_a_run_of_one_employee(repository):
    repository.save(PayRunResult(period=_period(), payslips=(_payslip("E0001"),)))
    register = repository.get_register(_period().start)
    assert len(register.payslips) == 1
