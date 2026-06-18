"""Bookkeeping table the migration runner uses to track applied migrations."""

from __future__ import annotations

import sqlite3

MIGRATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    sequence INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
"""


def ensure_migrations_table(connection: sqlite3.Connection) -> None:
    connection.execute(MIGRATIONS_TABLE_SQL)
