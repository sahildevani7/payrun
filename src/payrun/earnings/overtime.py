"""Overtime earnings: a flat multiplier on hourly pay above a weekly threshold."""

from __future__ import annotations

from decimal import Decimal

from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import ValidationError
from payrun.hours import Hours
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation
from payrun.people.employee import Employee
from payrun.rate import Rate
from payrun.rounding import RoundingMode, round_to_exponent

CODE = EarningCode("OVERTIME")


class OvertimeEarningCalculator:
    code = CODE

    def __init__(self, weekly_threshold: Hours, multiplier: Rate) -> None:
        self._weekly_threshold = weekly_threshold
        self._multiplier = multiplier

    @property
    def weekly_threshold(self) -> Hours:
        return self._weekly_threshold

    def calculate(self, employee: Employee, hours: Hours) -> EarningLine:
        if not isinstance(employee.compensation, HourlyCompensation):
            raise ValidationError("overtime earnings require hourly compensation")

        excess = hours.value - self._weekly_threshold.value
        overtime_hours = Hours(excess) if excess > 0 else Hours.zero()

        rate = employee.compensation.hourly_rate
        raw = rate.amount * self._multiplier.value * overtime_hours.value
        amount = Money(
            round_to_exponent(raw, rate.exponent, RoundingMode.HALF_UP), rate.currency
        )
        return EarningLine(code=self.code, amount=amount, hours=overtime_hours)


def default_calculator() -> OvertimeEarningCalculator:
    return OvertimeEarningCalculator(
        weekly_threshold=Hours(Decimal(40)), multiplier=Rate(Decimal("1.5"))
    )
