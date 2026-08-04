"""A progressive tax bracket table and the slice computation over it.

Brackets are sorted ascending by threshold. Each bracket's marginal rate
applies to the slice of income between its threshold and the next bracket's
threshold, or to everything above it for the top bracket. Each bracket's
raw tax is accumulated unrounded and the total is rounded once, so
per-bracket rounding never compounds.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from payrun.errors import ValidationError
from payrun.money import Money
from payrun.rate import Rate
from payrun.rounding import RoundingMode, round_to_exponent


@dataclass(frozen=True, slots=True)
class TaxBracket:
    threshold: Money
    rate: Rate


def validate_ascending(brackets: Sequence[TaxBracket]) -> None:
    """Raise if `brackets` is not sorted strictly ascending by threshold,
    or does not start at zero. `compute_tax` assumes this ordering; nothing
    downstream re-checks it once a bracket table has passed here.
    """
    if not brackets:
        raise ValidationError("a bracket table requires at least one bracket")
    if brackets[0].threshold.amount != 0:
        raise ValidationError("the first bracket must start at a zero threshold")
    for earlier, later in zip(brackets, brackets[1:], strict=False):
        if earlier.threshold.currency != later.threshold.currency:
            raise ValidationError("all brackets must share the same currency")
        if later.threshold.amount <= earlier.threshold.amount:
            raise ValidationError("bracket thresholds must be strictly ascending")


def compute_tax(taxable_income: Money, brackets: Sequence[TaxBracket]) -> Money:
    if not brackets:
        raise ValidationError("compute_tax requires at least one bracket")

    currency = taxable_income.currency
    raw_total = Decimal(0)
    for index, bracket in enumerate(brackets):
        if bracket.threshold.currency != currency:
            raise ValidationError("bracket currency does not match taxable_income currency")
        slice_start = bracket.threshold.amount
        if taxable_income.amount <= slice_start:
            continue
        has_next = index + 1 < len(brackets)
        slice_end = brackets[index + 1].threshold.amount if has_next else taxable_income.amount
        slice_end = min(slice_end, taxable_income.amount)
        slice_amount = slice_end - slice_start
        if slice_amount <= 0:
            continue
        raw_total += bracket.rate.value * slice_amount

    rounded = round_to_exponent(raw_total, taxable_income.exponent, RoundingMode.HALF_UP)
    return Money(rounded, currency)
