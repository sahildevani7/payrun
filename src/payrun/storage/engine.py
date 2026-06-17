"""SQLite connection management.

The only place `sqlite3.connect` is called directly. Every connection uses
`sqlite3.Row` for column access by name and has foreign keys enabled.
"""

from __future__ import annotations

import sqlite3


def connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
