"""Line-by-line content for a pay-run register, independent of output format."""

from __future__ import annotations

from payrun.run.result import PayRunResult


def register_lines(result: PayRunResult) -> list[str]:
    lines = [f"Pay Run Register: {result.period}"]
    for payslip in result.payslips:
        lines.append(f"{payslip.employee_id}: gross={payslip.gross} net={payslip.net}")
    if result.payslips:
        totals = result.totals()
        lines.append(f"TOTAL: gross={totals.gross} net={totals.net}")
        if any(payslip.employer_contributions for payslip in result.payslips):
            lines.append(f"TOTAL EMPLOYER CONTRIBUTIONS: {totals.employer_contributions}")
    return lines
