"""The output of a pay run: one pay slip per employee, plus run totals."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from payrun.calendarx.period import PayPeriod
from payrun.deductions.line import DeductionLine
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError, ValidationError
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
class RunTotals:
    gross: Money
    net: Money
    employer_contributions: Money


@dataclass(frozen=True, slots=True)
class PayRunResult:
    period: PayPeriod
    payslips: tuple[PaySlip, ...]

    def payslip_for(self, employee_id: EmployeeId) -> PaySlip:
        for payslip in self.payslips:
            if payslip.employee_id == employee_id:
                return payslip
        raise NotFoundError(f"no payslip for employee {employee_id}")

    def totals(self) -> RunTotals:
        if not self.payslips:
            raise ValidationError("totals require at least one payslip")
        currency = self.payslips[0].gross.currency
        return RunTotals(
            gross=_sum_money(currency, (payslip.gross for payslip in self.payslips)),
            net=_sum_money(currency, (payslip.net for payslip in self.payslips)),
            employer_contributions=_sum_money(
                currency,
                (
                    line.amount
                    for payslip in self.payslips
                    for line in payslip.employer_contributions
                ),
            ),
        )


def _sum_money(currency: str, amounts: Iterable[Money]) -> Money:
    total = Money.zero(currency)
    for amount in amounts:
        total = total + amount
    return total
