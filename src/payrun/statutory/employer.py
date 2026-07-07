"""The employer's share of a statutory contribution, as a multiple of the
employee's contribution.
"""

from __future__ import annotations

from payrun.money import Money
from payrun.rate import Rate
from payrun.rounding import RoundingMode, round_to_exponent


def employer_share(employee_contribution: Money, multiplier: Rate) -> Money:
    raw = employee_contribution.amount * multiplier.value
    rounded = round_to_exponent(raw, employee_contribution.exponent, RoundingMode.HALF_UP)
    return Money(rounded, employee_contribution.currency)
