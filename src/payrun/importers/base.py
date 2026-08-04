"""A parsed timesheet row, the importer seam, and hours aggregation."""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from payrun.errors import ImporterError
from payrun.hours import Hours
from payrun.ids import EmployeeId


@dataclass(frozen=True, slots=True)
class TimesheetEntry:
    employee_id: EmployeeId
    work_date: dt.date
    hours: Hours


@runtime_checkable
class Importer(Protocol):
    name: str

    def parse(self, content: str) -> list[TimesheetEntry]: ...


def aggregate_hours(entries: Sequence[TimesheetEntry]) -> dict[EmployeeId, Hours]:
    totals: dict[EmployeeId, Hours] = {}
    for entry in entries:
        totals[entry.employee_id] = totals.get(entry.employee_id, Hours.zero()) + entry.hours
    return totals


def total_hours(entries: Sequence[TimesheetEntry]) -> Hours:
    """The sum of every entry's hours, across every employee."""
    total = Hours.zero()
    for entry in entries:
        total = total + entry.hours
    return total


def parse_file(importer: Importer, path: Path) -> list[TimesheetEntry]:
    """Read `path` and parse it with `importer`, wrapping a read failure
    in `ImporterError` so callers only need to handle one exception type.
    """
    try:
        content = path.read_text()
    except OSError as exc:
        raise ImporterError(f"cannot read {path}: {exc}") from exc
    return importer.parse(content)
