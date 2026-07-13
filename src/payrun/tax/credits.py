"""The basic credit, applied against computed tax and never below zero."""

from __future__ import annotations

from payrun.money import Money


def apply_credit(tax: Money, credit: Money) -> Money:
    remaining = tax - credit
    return remaining if remaining.amount > 0 else Money.zero(tax.currency)
