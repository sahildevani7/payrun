"""A parsed timesheet row, the importer seam, and hours aggregation."""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

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
