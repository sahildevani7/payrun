"""Add indices for the lookups the repositories actually run.

`SqliteEmployeeRepository.list_by_frequency` filters on `frequency`,
`list_active_on` filters on `hire_date` and `termination_date`, and
`SqliteTimesheetRepository.hours_for_period` filters on `work_date`. None
of these needed an index while the tables were small in tests, but a real
employer's history grows, and a forward-only migration is the only place
to add one without touching the tables that already exist.
"""

from __future__ import annotations

import sqlite3

NAME = "0003_add_indices"

_SQL = """
CREATE INDEX idx_employees_frequency ON employees(frequency);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
CREATE INDEX idx_employees_termination_date ON employees(termination_date);
CREATE INDEX idx_timesheet_entries_work_date ON timesheet_entries(work_date);
"""


def up(connection: sqlite3.Connection) -> None:
    connection.executescript(_SQL)
