"""The set of earning calculators a pay run can draw on.

This is a seam: any object implementing `EarningCalculator` can be
registered. The base repository registers exactly two — regular and
overtime.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError, ValidationError
from payrun.hours import Hours
from payrun.people.employee import Employee


@runtime_checkable
class EarningCalculator(Protocol):
    code: EarningCode

    def calculate(self, employee: Employee, hours: Hours) -> EarningLine: ...


class EarningRegistry:
    def __init__(self) -> None:
        self._calculators: dict[EarningCode, EarningCalculator] = {}

    def register(self, calculator: EarningCalculator) -> None:
        if calculator.code in self._calculators:
            raise ValidationError(f"earning code {calculator.code} is already registered")
        self._calculators[calculator.code] = calculator

    def get(self, code: EarningCode) -> EarningCalculator:
        try:
            return self._calculators[code]
        except KeyError:
            raise NotFoundError(f"no earning calculator registered for {code}") from None

    def codes(self) -> list[EarningCode]:
        return sorted(self._calculators, key=str)
