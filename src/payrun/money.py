"""Money over `Decimal`. No `float` ever touches an amount.

Each currency carries a minor-unit exponent (2 for cents, 0 for a currency
with no minor unit). Rounding is never implicit: use `rounded()` with an
explicit `RoundingMode` before anything that needs a currency-exact figure.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import ROUND_FLOOR, Decimal

from payrun.errors import CurrencyMismatchError, ValidationError
from payrun.rounding import RoundingMode, round_to_exponent

CURRENCY_EXPONENTS: dict[str, int] = {
    "USD": 2,
    "CAD": 2,
    "GBP": 2,
    "EUR": 2,
    "JPY": 0,
}

_Numeric = int | Decimal


class Money:
    """An exact amount of a single currency."""

    __slots__ = ("_amount", "_currency")

    def __init__(self, amount: Decimal, currency: str = "USD") -> None:
        if not isinstance(amount, Decimal):
            raise ValidationError("Money amount must be a Decimal")
        if currency not in CURRENCY_EXPONENTS:
            raise ValidationError(f"unknown currency {currency!r}")
        self._amount = amount
        self._currency = currency

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def exponent(self) -> int:
        return CURRENCY_EXPONENTS[self._currency]

    @classmethod
    def zero(cls, currency: str = "USD") -> Money:
        return cls(Decimal(0), currency)

    @classmethod
    def from_minor_units(cls, units: int, currency: str = "USD") -> Money:
        if currency not in CURRENCY_EXPONENTS:
            raise ValidationError(f"unknown currency {currency!r}")
        quantum = Decimal(1).scaleb(-CURRENCY_EXPONENTS[currency])
        return cls(Decimal(units) * quantum, currency)

    def rounded(self, mode: RoundingMode) -> Money:
        return Money(round_to_exponent(self._amount, self.exponent, mode), self._currency)

    def to_minor_units(self) -> int:
        quantum = Decimal(1).scaleb(-self.exponent)
        if (self._amount / quantum) != (self._amount / quantum).to_integral_value():
            raise ValidationError(
                f"{self._amount} is not rounded to {self._currency}'s minor unit"
            )
        return int(self._amount.scaleb(self.exponent))

    def _check_currency(self, other: Money) -> None:
        if self._currency != other._currency:
            raise CurrencyMismatchError(self._currency, other._currency)

    def __add__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def __neg__(self) -> Money:
        return Money(-self._amount, self._currency)

    def __mul__(self, scalar: _Numeric) -> Money:
        if not isinstance(scalar, int | Decimal) or isinstance(scalar, bool):
            raise ValidationError("Money may only be scaled by an int or Decimal")
        return Money(self._amount * Decimal(scalar), self._currency)

    __rmul__ = __mul__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._currency == other._currency and self._amount == other._amount

    def __hash__(self) -> int:
        return hash((self._currency, self._amount))

    def __lt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self._amount < other._amount

    def __le__(self, other: Money) -> bool:
        self._check_currency(other)
        return self._amount <= other._amount

    def __gt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self._amount > other._amount

    def __ge__(self, other: Money) -> bool:
        self._check_currency(other)
        return self._amount >= other._amount

    def __repr__(self) -> str:
        return f"Money({self._amount!r}, {self._currency!r})"

    def __str__(self) -> str:
        return f"{self._amount} {self._currency}"


def allocate(total: Money, weights: Sequence[_Numeric]) -> list[Money]:
    """Split `total` proportionally to `weights`, largest-remainder method.

    `total` must already be rounded to its currency's minor unit. The shares
    sum exactly to `total`. Ties in the remainder distribution go to the
    entry with the larger weighted fraction, then to the lower index.
    """
    if not weights:
        raise ValidationError("allocate requires at least one weight")
    decimal_weights = [Decimal(w) for w in weights]
    if any(w < 0 for w in decimal_weights):
        raise ValidationError("allocate weights must be non-negative")
    weight_sum = sum(decimal_weights)
    if weight_sum <= 0:
        raise ValidationError("allocate weights must sum to a positive value")

    minor_total = total.to_minor_units()
    raw_shares = [Decimal(minor_total) * w / weight_sum for w in decimal_weights]
    floors = [int(share.to_integral_value(rounding=ROUND_FLOOR)) for share in raw_shares]
    remainder = minor_total - sum(floors)

    fractions = [share - floor for share, floor in zip(raw_shares, floors, strict=True)]
    order = sorted(range(len(decimal_weights)), key=lambda i: (-fractions[i], i))

    shares = list(floors)
    for i in order[:remainder]:
        shares[i] += 1

    return [Money.from_minor_units(units, total.currency) for units in shares]
