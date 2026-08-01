"""Pension contribution: rate over a per-period exemption, capped at the
annual maximum.

The caller supplies year-to-date contributions so far. This calculator caps
the current period's contribution at whatever room remains under the annual
maximum, so the running total across a year never exceeds it.
"""

from __future__ import annotations

from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.money import Money
from payrun.rounding import RoundingMode, round_to_exponent
from payrun.statutory.tables import PensionParameters


def annual_max_contribution(params: PensionParameters) -> Money:
    taxable = params.ceiling_annual - params.exemption_annual
    raw = params.rate.of(taxable)
    return Money(round_to_exponent(raw, taxable.exponent, RoundingMode.HALF_UP), taxable.currency)


class PensionCalculator:
    def __init__(self, params: PensionParameters, frequency: Frequency) -> None:
        self._params = params
        periods = Decimal(frequency.periods_per_year)
        exemption = params.exemption_annual
        raw_exemption = exemption.amount / periods
        rounded_exemption = round_to_exponent(
            raw_exemption, exemption.exponent, RoundingMode.HALF_UP
        )
        self._period_exemption = Money(rounded_exemption, exemption.currency)
        self._annual_max = annual_max_contribution(params)

    def calculate(self, gross: Money, ytd_contribution: Money) -> Money:
        pensionable = gross - self._period_exemption
        if pensionable.amount < 0:
            pensionable = Money.zero(gross.currency)
        raw = self._params.rate.of(pensionable)
        contribution = Money(
            round_to_exponent(raw, gross.exponent, RoundingMode.HALF_UP), gross.currency
        )
        remaining_room = self._annual_max - ytd_contribution
        if remaining_room.amount < 0:
            remaining_room = Money.zero(gross.currency)
        return contribution if contribution <= remaining_room else remaining_room
