"""A deduction equal to a fixed percentage of gross pay."""

from __future__ import annotations

from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.money import Money
from payrun.rate import Rate
from payrun.rounding import RoundingMode, round_to_exponent


class PercentageDeductionCalculator:
    def __init__(self, code: DeductionCode, rate: Rate) -> None:
        self.code = code
        self._rate = rate

    def calculate(self, gross: Money) -> DeductionLine:
        raw = self._rate.of(gross)
        rounded = round_to_exponent(raw, gross.exponent, RoundingMode.HALF_UP)
        return DeductionLine(code=self.code, amount=Money(rounded, gross.currency))
