"""Year-to-date accumulators: gross, pension, insurance, and tax withheld.

Four buckets, one per employee. Each pay run's contribution amounts feed in
here so the next period's statutory calculators know how much room remains
under an annual ceiling.
"""

from __future__ import annotations

from dataclasses import dataclass

from payrun.errors import CurrencyMismatchError
from payrun.ids import EmployeeId
from payrun.money import Money


@dataclass(frozen=True, slots=True)
class YtdAccumulator:
    gross: Money
    pension: Money
    insurance: Money
    tax: Money

    @classmethod
    def zero(cls, currency: str) -> YtdAccumulator:
        return cls(
            gross=Money.zero(currency),
            pension=Money.zero(currency),
            insurance=Money.zero(currency),
            tax=Money.zero(currency),
        )

    def plus(self, gross: Money, pension: Money, insurance: Money, tax: Money) -> YtdAccumulator:
        return YtdAccumulator(
            gross=self.gross + gross,
            pension=self.pension + pension,
            insurance=self.insurance + insurance,
            tax=self.tax + tax,
        )


class YtdStore:
    def __init__(self, currency: str) -> None:
        self._currency = currency
        self._data: dict[EmployeeId, YtdAccumulator] = {}

    def get(self, employee_id: EmployeeId) -> YtdAccumulator:
        return self._data.get(employee_id, YtdAccumulator.zero(self._currency))

    def record(
        self,
        employee_id: EmployeeId,
        gross: Money,
        pension: Money,
        insurance: Money,
        tax: Money,
    ) -> None:
        if gross.currency != self._currency:
            raise CurrencyMismatchError(self._currency, gross.currency)
        self._data[employee_id] = self.get(employee_id).plus(gross, pension, insurance, tax)
