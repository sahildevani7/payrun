"""Periodic withholding for regular pay: the annualized method.

The period's gross is multiplied out to an annual figure, taxed against the
bracket table, reduced by the basic credit, and divided back down to a
per-period withholding amount. This is the only withholding method the base
repository ships — a bonus method that switches and caps differently is a
separate concern.
"""

from __future__ import annotations

from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.money import Money
from payrun.rounding import RoundingMode, round_to_exponent
from payrun.statutory.tables import TaxParameters
from payrun.tax.brackets import compute_tax
from payrun.tax.credits import apply_credit


class WithholdingCalculator:
    def __init__(self, params: TaxParameters, frequency: Frequency) -> None:
        self._params = params
        self._periods = frequency.periods_per_year

    def calculate(self, gross: Money) -> Money:
        annualized = gross * self._periods
        annual_tax = compute_tax(annualized, self._params.brackets)
        credited = apply_credit(annual_tax, self._params.basic_credit_annual)
        raw_periodic = credited.amount / Decimal(self._periods)
        rounded = round_to_exponent(raw_periodic, gross.exponent, RoundingMode.HALF_UP)
        return Money(rounded, gross.currency)
