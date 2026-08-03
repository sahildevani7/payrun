import datetime as dt
from decimal import Decimal

from payrun.calendarx.period import PayPeriod
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.reporting.register import register_lines
from payrun.run.result import PayRunResult, PaySlip


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )


def _payslip(employee_id: str, gross: str, net: str) -> PaySlip:
    return PaySlip(
        employee_id=EmployeeId(employee_id),
        period=_period(),
        earnings=(),
        deductions=(),
        employer_contributions=(),
        gross=Money(Decimal(gross), "USD"),
        net=Money(Decimal(net), "USD"),
    )


def test_header_names_the_period():
    result = PayRunResult(period=_period(), payslips=())
    lines = register_lines(result)
    assert lines[0] == "Pay Run Register: 2026-03-01..2026-03-15"


def test_one_row_per_payslip_in_payslip_order():
    result = PayRunResult(
        period=_period(),
        payslips=(
            _payslip("E0001", "2000.00", "1800.00"),
            _payslip("E0002", "3000.00", "2600.00"),
        ),
    )
    lines = register_lines(result)
    assert lines[1] == "E0001: gross=2000.00 USD net=1800.00 USD"
    assert lines[2] == "E0002: gross=3000.00 USD net=2600.00 USD"


def test_empty_run_has_only_the_header():
    result = PayRunResult(period=_period(), payslips=())
    assert register_lines(result) == ["Pay Run Register: 2026-03-01..2026-03-15"]


def test_register_has_one_line_per_payslip_plus_header_and_total():
    result = PayRunResult(
        period=_period(),
        payslips=(
            _payslip("E0001", "2000.00", "1800.00"),
            _payslip("E0002", "3000.00", "2600.00"),
            _payslip("E0003", "1500.00", "1350.00"),
        ),
    )
    assert len(register_lines(result)) == 5


def test_register_total_sums_gross_and_net_across_employees():
    result = PayRunResult(
        period=_period(),
        payslips=(
            _payslip("E0001", "2000.00", "1800.00"),
            _payslip("E0002", "3000.00", "2600.00"),
        ),
    )
    lines = register_lines(result)
    assert lines[-1] == "TOTAL: gross=5000.00 USD net=4400.00 USD"
