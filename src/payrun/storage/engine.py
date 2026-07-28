"""SQLite connection management.

The only place `sqlite3.connect` is called directly. Every connection uses
`sqlite3.Row` for column access by name and has foreign keys enabled.
"""

from __future__ import annotations

import sqlite3

from payrun.storage.migrations.runner import MigrationRunner


def connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def connect_and_migrate(path: str) -> sqlite3.Connection:
    connection = connect(path)
    MigrationRunner().run(connection)
    return connection
