"""An exact percentage or fractional rate over `Decimal`.

A rate is never a `float` and never a bare string. `Rate.of` returns the
exact, unrounded product against a `Money` amount — rounding, if any, is the
caller's explicit decision at the point it is needed.
"""

from __future__ import annotations

from decimal import Decimal

from payrun.errors import ValidationError
from payrun.money import Money


class Rate:
    """A non-negative fractional rate, e.g. 0.062 for 6.2%."""

    __slots__ = ("_value",)

    def __init__(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise ValidationError("Rate value must be a Decimal")
        if value < 0:
            raise ValidationError("Rate value must be non-negative")
        self._value = value

    @classmethod
    def from_percent(cls, percent: Decimal) -> Rate:
        if not isinstance(percent, Decimal):
            raise ValidationError("Rate percent must be a Decimal")
        return cls(percent / Decimal(100))

    @classmethod
    def zero(cls) -> Rate:
        return cls(Decimal(0))

    @property
    def value(self) -> Decimal:
        return self._value

    def of(self, money: Money) -> Decimal:
        """The exact, unrounded amount this rate represents of `money`."""
        return money.amount * self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rate):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __lt__(self, other: Rate) -> bool:
        return self._value < other._value

    def __le__(self, other: Rate) -> bool:
        return self._value <= other._value

    def __gt__(self, other: Rate) -> bool:
        return self._value > other._value

    def __ge__(self, other: Rate) -> bool:
        return self._value >= other._value

    def __repr__(self) -> str:
        return f"Rate({self._value!r})"
