"""The one shipped timesheet dialect: a plain CSV with a fixed header.

Columns, in order: `employee_id`, `work_date` (ISO 8601), `hours` (a
quarter-hour decimal). Any deviation from the exact header is rejected —
this importer does not sniff or guess a dialect.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
from decimal import Decimal, InvalidOperation

from payrun.errors import ImporterError, ValidationError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.importers.base import TimesheetEntry

FIELDNAMES = ("employee_id", "work_date", "hours")


class TimesheetCsvImporter:
    name = "timesheet_csv"

    def parse(self, content: str) -> list[TimesheetEntry]:
        reader = csv.DictReader(io.StringIO(content))
        if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDNAMES:
            raise ImporterError(f"expected header {FIELDNAMES}, got {reader.fieldnames}")

        entries = []
        for line_number, row in enumerate(reader, start=2):
            entries.append(self._parse_row(row, line_number))
        return entries

    def _parse_row(self, row: dict[str, str], line_number: int) -> TimesheetEntry:
        try:
            employee_id = EmployeeId(row["employee_id"])
            work_date = dt.date.fromisoformat(row["work_date"])
            hours = Hours(Decimal(row["hours"]))
        except (ValidationError, ValueError, InvalidOperation, TypeError) as exc:
            raise ImporterError(f"line {line_number}: {exc}") from exc
        return TimesheetEntry(employee_id=employee_id, work_date=work_date, hours=hours)
