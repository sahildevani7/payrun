"""Exact quarter-hour math over `Decimal`.

Every `Hours` value is a non-negative multiple of a quarter hour. This is
the unit timesheets are recorded in and the unit earnings calculations
consume, so the constraint is enforced once at construction rather than
re-checked throughout the codebase.
"""

from __future__ import annotations

from decimal import Decimal

from payrun.errors import ValidationError

_QUANTUM = Decimal("0.25")


class Hours:
    __slots__ = ("_value",)

    def __init__(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise ValidationError("Hours value must be a Decimal")
        if value < 0:
            raise ValidationError("Hours value must be non-negative")
        if (value / _QUANTUM) != (value / _QUANTUM).to_integral_value():
            raise ValidationError("Hours value must be a multiple of a quarter hour")
        self._value = value

    @classmethod
    def zero(cls) -> Hours:
        return cls(Decimal(0))

    @property
    def value(self) -> Decimal:
        return self._value

    def __add__(self, other: Hours) -> Hours:
        return Hours(self._value + other._value)

    def __sub__(self, other: Hours) -> Hours:
        return Hours(self._value - other._value)

    def __mul__(self, scalar: Decimal) -> Decimal:
        if not isinstance(scalar, Decimal):
            raise ValidationError("Hours may only be scaled by a Decimal")
        return self._value * scalar

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hours):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __lt__(self, other: Hours) -> bool:
        return self._value < other._value

    def __le__(self, other: Hours) -> bool:
        return self._value <= other._value

    def __gt__(self, other: Hours) -> bool:
        return self._value > other._value

    def __ge__(self, other: Hours) -> bool:
        return self._value >= other._value

    def __repr__(self) -> str:
        return f"Hours({self._value!r})"

    def __str__(self) -> str:
        return str(self._value)
