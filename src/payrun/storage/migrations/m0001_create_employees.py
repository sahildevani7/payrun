"""Create the `employees` table."""

from __future__ import annotations

import sqlite3

NAME = "0001_create_employees"

_SQL = """
CREATE TABLE employees (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    frequency TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    status TEXT NOT NULL,
    termination_date TEXT,
    compensation_type TEXT NOT NULL,
    compensation_amount TEXT NOT NULL,
    currency TEXT NOT NULL
)
"""


def up(connection: sqlite3.Connection) -> None:
    connection.execute(_SQL)
