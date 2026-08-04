import datetime as dt
from decimal import Decimal

import pytest

from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError, ValidationError
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


def _payslip(employee_id: str, gross: str = "2000.00", net: str = "1800.00") -> PaySlip:
    return PaySlip(
        employee_id=EmployeeId(employee_id),
        period=_period(),
        earnings=(EarningLine(EarningCode("REGULAR"), Money(Decimal(gross), "USD")),),
        deductions=(DeductionLine(DeductionCode("TAX"), Money(Decimal("200.00"), "USD")),),
        employer_contributions=(),
        gross=Money(Decimal(gross), "USD"),
        net=Money(Decimal(net), "USD"),
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


def test_empty_pay_run_result_has_no_payslips():
    result = PayRunResult(period=_period(), payslips=())
    assert result.payslips == ()


def test_payslip_for_finds_the_right_slip_among_several():
    result = PayRunResult(
        period=_period(), payslips=(_payslip("E0001"), _payslip("E0002"), _payslip("E0003"))
    )
    assert result.payslip_for(EmployeeId("E0003")).employee_id == EmployeeId("E0003")


def test_totals_sum_gross_and_net_across_payslips():
    result = PayRunResult(
        period=_period(),
        payslips=(_payslip("E0001", "2000.00", "1800.00"), _payslip("E0002", "3000.00", "2600.00")),
    )
    totals = result.totals()
    assert totals.gross == Money(Decimal("5000.00"), "USD")
    assert totals.net == Money(Decimal("4400.00"), "USD")


def test_totals_sum_employer_contributions_across_payslips():
    payslip = PaySlip(
        employee_id=EmployeeId("E0001"),
        period=_period(),
        earnings=(),
        deductions=(),
        employer_contributions=(
            DeductionLine(DeductionCode("PENSION"), Money(Decimal("100.00"), "USD")),
            DeductionLine(DeductionCode("INSURANCE"), Money(Decimal("50.00"), "USD")),
        ),
        gross=Money(Decimal("2000.00"), "USD"),
        net=Money(Decimal("1800.00"), "USD"),
    )
    totals = PayRunResult(period=_period(), payslips=(payslip,)).totals()
    assert totals.employer_contributions == Money(Decimal("150.00"), "USD")


def test_totals_are_zero_for_a_run_with_no_employer_contributions():
    totals = PayRunResult(period=_period(), payslips=(_payslip("E0001"),)).totals()
    assert totals.employer_contributions == Money.zero("USD")


def test_totals_preserve_the_currency():
    totals = PayRunResult(period=_period(), payslips=(_payslip("E0001"),)).totals()
    assert totals.gross.currency == "USD"
    assert totals.net.currency == "USD"


def test_totals_on_an_empty_run_raise_validation_error():
    result = PayRunResult(period=_period(), payslips=())
    with pytest.raises(ValidationError):
        result.totals()
