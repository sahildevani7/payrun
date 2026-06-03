"""Explicit rounding policy.

Rounding mode is never implicit. Callers pass a `RoundingMode` at the
boundary that requires one.
"""

from __future__ import annotations

import enum
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal


class RoundingMode(enum.Enum):
    HALF_UP = "HALF_UP"
    HALF_EVEN = "HALF_EVEN"


_DECIMAL_ROUNDING = {
    RoundingMode.HALF_UP: ROUND_HALF_UP,
    RoundingMode.HALF_EVEN: ROUND_HALF_EVEN,
}


def round_to_exponent(amount: Decimal, exponent: int, mode: RoundingMode) -> Decimal:
    """Round `amount` to `exponent` decimal places under `mode`.

    `exponent` is the number of digits after the decimal point, matching a
    currency's minor-unit exponent (2 for cents, 0 for a currency with no
    minor unit).
    """
    quantum = Decimal(1).scaleb(-exponent)
    return amount.quantize(quantum, rounding=_DECIMAL_ROUNDING[mode])


def round_half_up(amount: Decimal, exponent: int) -> Decimal:
    return round_to_exponent(amount, exponent, RoundingMode.HALF_UP)


def round_half_even(amount: Decimal, exponent: int) -> Decimal:
    return round_to_exponent(amount, exponent, RoundingMode.HALF_EVEN)
