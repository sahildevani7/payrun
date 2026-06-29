"""Regular earnings: an hourly rate times hours worked, or a salary slice."""

from __future__ import annotations

from decimal import Decimal

from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.hours import Hours
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation
from payrun.people.employee import Employee
from payrun.rounding import RoundingMode, round_to_exponent

CODE = EarningCode("REGULAR")


class RegularEarningCalculator:
    code = CODE

    def calculate(self, employee: Employee, hours: Hours) -> EarningLine:
        if isinstance(employee.compensation, HourlyCompensation):
            rate = employee.compensation.hourly_rate
            raw = rate.amount * hours.value
            amount = Money(
                round_to_exponent(raw, rate.exponent, RoundingMode.HALF_UP), rate.currency
            )
            return EarningLine(code=self.code, amount=amount, hours=hours)

        annual = employee.compensation.annual_amount
        periods = Decimal(employee.frequency.periods_per_year)
        raw = annual.amount / periods
        amount = Money(
            round_to_exponent(raw, annual.exponent, RoundingMode.HALF_UP), annual.currency
        )
        return EarningLine(code=self.code, amount=amount, hours=None)
