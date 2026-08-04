"""One earning entry on a pay statement: a code and a computed amount."""

from __future__ import annotations

from dataclasses import dataclass

from payrun.earnings.code import EarningCode
from payrun.errors import ValidationError
from payrun.hours import Hours
from payrun.money import Money


@dataclass(frozen=True, slots=True)
class EarningLine:
    code: EarningCode
    amount: Money
    hours: Hours | None = None

    def __post_init__(self) -> None:
        if self.amount.amount < 0:
            raise ValidationError("EarningLine amount must not be negative")

    def __str__(self) -> str:
        return f"{self.code}: {self.amount}"
