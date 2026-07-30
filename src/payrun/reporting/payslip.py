"""Line-by-line content for a single pay slip, independent of output format."""

from __future__ import annotations

from payrun.run.result import PaySlip


def payslip_lines(payslip: PaySlip) -> list[str]:
    lines = [
        f"Employee: {payslip.employee_id}",
        f"Period: {payslip.period}",
        "Earnings:",
    ]
    for earning in payslip.earnings:
        lines.append(f"  {earning.code}: {earning.amount}")
    lines.append("Deductions:")
    for deduction in payslip.deductions:
        lines.append(f"  {deduction.code}: {deduction.amount}")
    lines.append("Employer Contributions:")
    for contribution in payslip.employer_contributions:
        lines.append(f"  {contribution.code}: {contribution.amount}")
    lines.append(f"Gross: {payslip.gross}")
    lines.append(f"Net: {payslip.net}")
    return lines
