"""Shared formatting helpers for renderers.

Both `payslip.py` and `register.py` need to sum a column of `Money` values
into a total line. This is the one place that does it, so the two stay
consistent about how an empty column is summed and what currency the
result carries.
"""

from __future__ import annotations

from collections.abc import Iterable

from payrun.errors import ValidationError
from payrun.money import Money


def sum_amounts(amounts: Iterable[Money]) -> Money:
    total: Money | None = None
    for amount in amounts:
        total = amount if total is None else total + amount
    if total is None:
        raise ValidationError("sum_amounts requires at least one amount")
    return total
