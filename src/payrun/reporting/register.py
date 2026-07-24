"""Line-by-line content for a pay-run register, independent of output format."""

from __future__ import annotations

from payrun.run.result import PayRunResult


def register_lines(result: PayRunResult) -> list[str]:
    lines = [f"Pay Run Register: {result.period}"]
    for payslip in result.payslips:
        lines.append(f"{payslip.employee_id}: gross={payslip.gross} net={payslip.net}")
    return lines
