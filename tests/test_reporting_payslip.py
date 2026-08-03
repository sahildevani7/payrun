import datetime as dt
from decimal import Decimal

from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.reporting.payslip import payslip_lines
from payrun.run.result import PaySlip


def _payslip(employer_contributions: tuple[DeductionLine, ...] = ()) -> PaySlip:
    return PaySlip(
        employee_id=EmployeeId("E0007"),
        period=PayPeriod(
            start=dt.date(2026, 3, 1),
            end=dt.date(2026, 3, 15),
            pay_date=dt.date(2026, 3, 20),
            sequence=1,
        ),
        earnings=(EarningLine(EarningCode("REGULAR"), Money(Decimal("2000.00"), "USD")),),
        deductions=(DeductionLine(DeductionCode("TAX"), Money(Decimal("200.00"), "USD")),),
        employer_contributions=employer_contributions,
        gross=Money(Decimal("2000.00"), "USD"),
        net=Money(Decimal("1800.00"), "USD"),
    )


def test_includes_employee_and_period():
    lines = payslip_lines(_payslip())
    assert "Employee: E0007" in lines
    assert "Period: 2026-03-01..2026-03-15" in lines


def test_includes_each_earning_line():
    lines = payslip_lines(_payslip())
    assert "  REGULAR: 2000.00 USD" in lines


def test_includes_each_deduction_line():
    lines = payslip_lines(_payslip())
    assert "  TAX: 200.00 USD" in lines


def test_includes_gross_and_net():
    lines = payslip_lines(_payslip())
    assert "Gross: 2000.00 USD" in lines
    assert "Net: 1800.00 USD" in lines


def test_section_headers_present():
    lines = payslip_lines(_payslip())
    assert "Earnings:" in lines
    assert "Deductions:" in lines
    assert "Employer Contributions:" in lines


def test_includes_each_employer_contribution_line():
    employer_contributions = (
        DeductionLine(DeductionCode("PENSION"), Money(Decimal("100.00"), "USD")),
    )
    lines = payslip_lines(_payslip(employer_contributions))
    assert "  PENSION: 100.00 USD" in lines


def test_employer_contributions_section_present_even_when_empty():
    lines = payslip_lines(_payslip())
    index = lines.index("Employer Contributions:")
    assert lines[index + 1] == "Gross: 2000.00 USD"


def test_total_earnings_line_equals_gross():
    assert "  Total Earnings: 2000.00 USD" in payslip_lines(_payslip())


def test_total_deductions_line_sums_all_deduction_lines():
    assert "  Total Deductions: 200.00 USD" in payslip_lines(_payslip())


def test_total_employer_contributions_line_present_when_nonempty():
    employer_contributions = (
        DeductionLine(DeductionCode("PENSION"), Money(Decimal("100.00"), "USD")),
        DeductionLine(DeductionCode("INSURANCE"), Money(Decimal("35.00"), "USD")),
    )
    lines = payslip_lines(_payslip(employer_contributions))
    assert "  Total Employer Contributions: 135.00 USD" in lines


def test_no_total_employer_contributions_line_when_empty():
    lines = payslip_lines(_payslip())
    assert not any(line.startswith("  Total Employer Contributions") for line in lines)
