"""Line-by-line content for a pay-run register, independent of output format."""

from __future__ import annotations

from payrun.reporting.formatting import sum_amounts
from payrun.run.result import PayRunResult


def register_lines(result: PayRunResult) -> list[str]:
    lines = [f"Pay Run Register: {result.period}"]
    for payslip in result.payslips:
        lines.append(f"{payslip.employee_id}: gross={payslip.gross} net={payslip.net}")
    if result.payslips:
        total_gross = sum_amounts(payslip.gross for payslip in result.payslips)
        total_net = sum_amounts(payslip.net for payslip in result.payslips)
        lines.append(f"TOTAL: gross={total_gross} net={total_net}")
    return lines
