"""Line-by-line content for a single pay slip, independent of output format."""

from __future__ import annotations

from payrun.money import Money
from payrun.reporting.formatting import sum_amounts
from payrun.run.result import PaySlip


def payslip_lines(payslip: PaySlip) -> list[str]:
    currency = payslip.gross.currency
    lines = [
        f"Employee: {payslip.employee_id}",
        f"Period: {payslip.period}",
        "Earnings:",
    ]
    for earning in payslip.earnings:
        lines.append(f"  {earning.code}: {earning.amount}")
    lines.append(f"  Total Earnings: {payslip.gross}")

    lines.append("Deductions:")
    for deduction in payslip.deductions:
        lines.append(f"  {deduction.code}: {deduction.amount}")
    deduction_total = (
        sum_amounts(line.amount for line in payslip.deductions)
        if payslip.deductions
        else Money.zero(currency)
    )
    lines.append(f"  Total Deductions: {deduction_total}")

    lines.append("Employer Contributions:")
    for contribution in payslip.employer_contributions:
        lines.append(f"  {contribution.code}: {contribution.amount}")
    if payslip.employer_contributions:
        employer_total = sum_amounts(line.amount for line in payslip.employer_contributions)
        lines.append(f"  Total Employer Contributions: {employer_total}")

    lines.append(f"Gross: {payslip.gross}")
    lines.append(f"Net: {payslip.net}")
    return lines
