"""A flat per-period deduction, independent of gross pay."""

from __future__ import annotations

from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.errors import CurrencyMismatchError
from payrun.money import Money


class FlatDeductionCalculator:
    def __init__(self, code: DeductionCode, amount: Money) -> None:
        self.code = code
        self._amount = amount

    def calculate(self, gross: Money) -> DeductionLine:
        if gross.currency != self._amount.currency:
            raise CurrencyMismatchError(gross.currency, self._amount.currency)
        return DeductionLine(code=self.code, amount=self._amount)
