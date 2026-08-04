"""Tax credits, applied against computed tax and never below zero."""

from __future__ import annotations

from payrun.money import Money


def apply_credits(tax: Money, *credits: Money) -> Money:
    total_credit = Money.zero(tax.currency)
    for credit in credits:
        total_credit = total_credit + credit
    remaining = tax - total_credit
    return remaining if remaining.amount > 0 else Money.zero(tax.currency)


def apply_credit(tax: Money, credit: Money) -> Money:
    return apply_credits(tax, credit)
