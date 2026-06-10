"""A single pay period: the span of earnings and the date they are paid."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from payrun.errors import ValidationError


@dataclass(frozen=True, slots=True, order=True)
class PayPeriod:
    start: dt.date
    end: dt.date
    pay_date: dt.date
    sequence: int

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValidationError("PayPeriod end must not precede start")
        if self.pay_date < self.end:
            raise ValidationError("PayPeriod pay_date must not precede end")
        if self.sequence < 1:
            raise ValidationError("PayPeriod sequence must be a positive integer")

    @property
    def day_span(self) -> int:
        return (self.end - self.start).days + 1

    def contains(self, day: dt.date) -> bool:
        return self.start <= day <= self.end

    def __str__(self) -> str:
        return f"{self.start.isoformat()}..{self.end.isoformat()}"
