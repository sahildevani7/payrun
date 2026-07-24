"""The one shipped renderer: plain text."""

from __future__ import annotations

from payrun.reporting.payslip import payslip_lines
from payrun.reporting.register import register_lines
from payrun.run.result import PayRunResult, PaySlip


class TextRenderer:
    def render_payslip(self, payslip: PaySlip) -> str:
        return "\n".join(payslip_lines(payslip))

    def render_register(self, result: PayRunResult) -> str:
        return "\n".join(register_lines(result))
