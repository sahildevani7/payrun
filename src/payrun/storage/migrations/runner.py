"""Apply pending migrations, in order, exactly once each."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from payrun.errors import MigrationError
from payrun.storage.migrations import m0001_create_employees
from payrun.storage.schema import ensure_migrations_table


@dataclass(frozen=True, slots=True)
class Migration:
    name: str
    up: Callable[[sqlite3.Connection], None]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(m0001_create_employees.NAME, m0001_create_employees.up),
)


class MigrationRunner:
    def __init__(self, migrations: Sequence[Migration] = MIGRATIONS) -> None:
        names = [m.name for m in migrations]
        if len(names) != len(set(names)):
            raise MigrationError("migration names must be unique")
        self._migrations = tuple(migrations)

    def applied(self, connection: sqlite3.Connection) -> list[str]:
        ensure_migrations_table(connection)
        rows = connection.execute(
            "SELECT name FROM schema_migrations ORDER BY sequence"
        ).fetchall()
        return [row["name"] for row in rows]

    def run(self, connection: sqlite3.Connection) -> list[str]:
        ensure_migrations_table(connection)
        already_applied = set(self.applied(connection))
        newly_applied = []
        for sequence, migration in enumerate(self._migrations, start=1):
            if migration.name in already_applied:
                continue
            try:
                migration.up(connection)
                connection.execute(
                    "INSERT INTO schema_migrations (sequence, name) VALUES (?, ?)",
                    (sequence, migration.name),
                )
            except sqlite3.DatabaseError as exc:
                connection.rollback()
                raise MigrationError(f"migration {migration.name} failed: {exc}") from exc
            newly_applied.append(migration.name)
        connection.commit()
        return newly_applied
