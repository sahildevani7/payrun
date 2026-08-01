import datetime as dt
from decimal import Decimal

import pytest

from payrun.errors import ImporterError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.importers.base import TimesheetEntry, aggregate_hours
from payrun.importers.timesheet_csv import TimesheetCsvImporter


def test_parses_valid_rows():
    content = "employee_id,work_date,hours\nE0001,2026-03-02,8.00\nE0001,2026-03-03,7.50\n"
    entries = TimesheetCsvImporter().parse(content)
    assert entries == [
        TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 2), Hours(Decimal("8.00"))),
        TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 3), Hours(Decimal("7.50"))),
    ]


def test_empty_body_with_valid_header_parses_to_no_entries():
    assert TimesheetCsvImporter().parse("employee_id,work_date,hours\n") == []


def test_rejects_missing_header():
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse("id,date,hrs\nE0001,2026-03-02,8.00\n")


def test_rejects_reordered_header():
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse("work_date,employee_id,hours\n2026-03-02,E0001,8.00\n")


def test_rejects_invalid_date():
    content = "employee_id,work_date,hours\nE0001,not-a-date,8.00\n"
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse(content)


def test_rejects_invalid_hours():
    content = "employee_id,work_date,hours\nE0001,2026-03-02,not-a-number\n"
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse(content)


def test_rejects_hours_not_on_a_quarter_hour():
    content = "employee_id,work_date,hours\nE0001,2026-03-02,8.10\n"
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse(content)


def test_rejects_blank_employee_id():
    content = "employee_id,work_date,hours\n,2026-03-02,8.00\n"
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse(content)


def test_error_message_names_the_line_number():
    content = "employee_id,work_date,hours\nE0001,2026-03-02,8.00\nE0001,bad,8.00\n"
    with pytest.raises(ImporterError, match="line 3"):
        TimesheetCsvImporter().parse(content)


def test_importer_name_is_stable():
    assert TimesheetCsvImporter().name == "timesheet_csv"


def test_aggregate_hours_sums_per_employee():
    entries = [
        TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 2), Hours(Decimal("8.00"))),
        TimesheetEntry(EmployeeId("E0001"), dt.date(2026, 3, 3), Hours(Decimal("7.50"))),
        TimesheetEntry(EmployeeId("E0002"), dt.date(2026, 3, 2), Hours(Decimal("6.00"))),
    ]
    totals = aggregate_hours(entries)
    assert totals == {
        EmployeeId("E0001"): Hours(Decimal("15.50")),
        EmployeeId("E0002"): Hours(Decimal("6.00")),
    }


def test_aggregate_hours_of_empty_entries_is_empty_dict():
    assert aggregate_hours([]) == {}


def test_rejects_hours_column_with_negative_value():
    content = "employee_id,work_date,hours\nE0001,2026-03-02,-8.00\n"
    with pytest.raises(ImporterError):
        TimesheetCsvImporter().parse(content)


def test_parses_rows_for_multiple_employees():
    content = (
        "employee_id,work_date,hours\n"
        "E0001,2026-03-02,8.00\n"
        "E0002,2026-03-02,6.00\n"
    )
    entries = TimesheetCsvImporter().parse(content)
    assert {e.employee_id for e in entries} == {EmployeeId("E0001"), EmployeeId("E0002")}
