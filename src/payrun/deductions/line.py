"""One deduction entry on a pay statement: a code and a withheld amount."""

from __future__ import annotations

from dataclasses import dataclass

from payrun.deductions.code import DeductionCode
from payrun.errors import ValidationError
from payrun.money import Money


@dataclass(frozen=True, slots=True)
class DeductionLine:
    code: DeductionCode
    amount: Money

    def __post_init__(self) -> None:
        if self.amount.amount < 0:
            raise ValidationError("DeductionLine amount must not be negative")
