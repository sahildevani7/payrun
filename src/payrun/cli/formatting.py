"""A plain, fixed-width table for `employees list` and similar output.

No color, no box-drawing characters — this is meant to be readable in any
terminal and easy to pipe into another tool.
"""

from __future__ import annotations

from collections.abc import Sequence

from payrun.errors import ValidationError


def format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    if any(len(row) != len(headers) for row in rows):
        raise ValidationError("every row must have the same number of columns as the headers")

    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    lines = [_format_row(headers, widths)]
    lines.append("-+-".join("-" * width for width in widths))
    for row in rows:
        lines.append(_format_row(row, widths))
    return "\n".join(lines)


def _format_row(cells: Sequence[str], widths: Sequence[int]) -> str:
    return " | ".join(cell.ljust(width) for cell, width in zip(cells, widths, strict=True))
