"""Create tables for imported timesheet entries, pay slips, and YTD accumulators."""

from __future__ import annotations

import sqlite3

NAME = "0002_create_run_tables"

_SQL = """
CREATE TABLE timesheet_entries (
    employee_id TEXT NOT NULL,
    work_date TEXT NOT NULL,
    hours TEXT NOT NULL,
    PRIMARY KEY (employee_id, work_date)
);

CREATE TABLE payslips (
    period_start TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    period_end TEXT NOT NULL,
    pay_date TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    gross TEXT NOT NULL,
    net TEXT NOT NULL,
    currency TEXT NOT NULL,
    earnings_json TEXT NOT NULL,
    deductions_json TEXT NOT NULL,
    employer_contributions_json TEXT NOT NULL,
    PRIMARY KEY (period_start, employee_id)
);

CREATE TABLE ytd_accumulators (
    employee_id TEXT PRIMARY KEY,
    currency TEXT NOT NULL,
    gross TEXT NOT NULL,
    pension TEXT NOT NULL,
    insurance TEXT NOT NULL,
    tax TEXT NOT NULL
);
"""


def up(connection: sqlite3.Connection) -> None:
    connection.executescript(_SQL)
