import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.run.result import PayRunResult, PaySlip


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
        earnings=(EarningLine(EarningCode("REGULAR"), Money(Decimal("2000.00"), "USD")),),
        deductions=(DeductionLine(DeductionCode("TAX"), Money(Decimal("200.00"), "USD")),),
        employer_contributions=(),
        gross=Money(Decimal("2000.00"), "USD"),
        net=Money(Decimal("1800.00"), "USD"),
    )


def test_payslip_for_returns_the_matching_slip():
    result = PayRunResult(period=_period(), payslips=(_payslip("E0001"), _payslip("E0002")))
    assert result.payslip_for(EmployeeId("E0002")).employee_id == EmployeeId("E0002")


def test_payslip_for_missing_employee_raises_not_found():
    result = PayRunResult(period=_period(), payslips=(_payslip("E0001"),))
    with pytest.raises(NotFoundError):
        result.payslip_for(EmployeeId("E9999"))


def test_payslip_holds_gross_and_net():
    payslip = _payslip("E0001")
    assert payslip.gross == Money(Decimal("2000.00"), "USD")
    assert payslip.net == Money(Decimal("1800.00"), "USD")
