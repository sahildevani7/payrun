"""A premium calculated as a flat rate of gross pay, capped at an annual maximum."""

from __future__ import annotations

from payrun.money import Money
from payrun.rounding import RoundingMode, round_to_exponent
from payrun.statutory.tables import InsuranceParameters


class InsuranceCalculator:
    def __init__(self, params: InsuranceParameters) -> None:
        self._params = params

    def calculate(self, gross: Money, ytd_premium: Money) -> Money:
        raw = self._params.rate.of(gross)
        rounded = round_to_exponent(raw, gross.exponent, RoundingMode.HALF_UP)
        premium = Money(rounded, gross.currency)
        remaining_room = self._params.annual_maximum - ytd_premium
        if remaining_room.amount < 0:
            remaining_room = Money.zero(gross.currency)
        return premium if premium <= remaining_room else remaining_room
