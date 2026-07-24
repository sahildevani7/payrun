"""The rendering seam: any object implementing this protocol can render a
pay slip and a pay-run register. The base repository ships exactly one
implementation, `text.TextRenderer`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from payrun.run.result import PayRunResult, PaySlip


@runtime_checkable
class Renderer(Protocol):
    def render_payslip(self, payslip: PaySlip) -> str: ...

    def render_register(self, result: PayRunResult) -> str: ...
