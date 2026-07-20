"""The output of a pay run: one pay slip per employee."""

from __future__ import annotations

from dataclasses import dataclass

from payrun.calendarx.period import PayPeriod
from payrun.deductions.line import DeductionLine
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError
from payrun.ids import EmployeeId
from payrun.money import Money


@dataclass(frozen=True, slots=True)
class PaySlip:
    employee_id: EmployeeId
    period: PayPeriod
    earnings: tuple[EarningLine, ...]
    deductions: tuple[DeductionLine, ...]
    employer_contributions: tuple[DeductionLine, ...]
    gross: Money
    net: Money


@dataclass(frozen=True, slots=True)
class PayRunResult:
    period: PayPeriod
    payslips: tuple[PaySlip, ...]

    def payslip_for(self, employee_id: EmployeeId) -> PaySlip:
        for payslip in self.payslips:
            if payslip.employee_id == employee_id:
                return payslip
        raise NotFoundError(f"no payslip for employee {employee_id}")
