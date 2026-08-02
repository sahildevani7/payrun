"""The set of earning calculators a pay run can draw on.

This is a seam: any object implementing `EarningCalculator` can be
registered. The base repository registers exactly two — regular and
overtime.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.earnings.overtime import OvertimeEarningCalculator
from payrun.earnings.overtime import default_calculator as default_overtime_calculator
from payrun.earnings.regular import RegularEarningCalculator
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


def default_registry(
    overtime_calculator: OvertimeEarningCalculator | None = None,
) -> EarningRegistry:
    """The registry every pay run needs at minimum: regular and overtime.

    Pass `overtime_calculator` when the caller needs a non-default weekly
    threshold or multiplier — callers that also cap regular hours at a
    threshold (see `run.factory.build_engine`) must use the same instance
    for both, or the two would disagree about which hours are overtime.
    """
    registry = EarningRegistry()
    registry.register(RegularEarningCalculator())
    registry.register(overtime_calculator or default_overtime_calculator())
    return registry
