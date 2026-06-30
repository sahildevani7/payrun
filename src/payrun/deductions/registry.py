"""The set of voluntary deduction calculators a pay run can draw on.

This is a seam: any object implementing `DeductionCalculator` can be
registered. The base repository registers exactly two — flat and
percentage.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.errors import NotFoundError, ValidationError
from payrun.money import Money


@runtime_checkable
class DeductionCalculator(Protocol):
    code: DeductionCode

    def calculate(self, gross: Money) -> DeductionLine: ...


class DeductionRegistry:
    def __init__(self) -> None:
        self._calculators: dict[DeductionCode, DeductionCalculator] = {}

    def register(self, calculator: DeductionCalculator) -> None:
        if calculator.code in self._calculators:
            raise ValidationError(f"deduction code {calculator.code} is already registered")
        self._calculators[calculator.code] = calculator

    def get(self, code: DeductionCode) -> DeductionCalculator:
        try:
            return self._calculators[code]
        except KeyError:
            raise NotFoundError(f"no deduction calculator registered for {code}") from None

    def codes(self) -> list[DeductionCode]:
        return sorted(self._calculators, key=str)
