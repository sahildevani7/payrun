"""`payrun import`: load a timesheet CSV into storage."""

from __future__ import annotations

import argparse
from pathlib import Path

from payrun.config import Config
from payrun.errors import ImporterError
from payrun.importers.timesheet_csv import TimesheetCsvImporter
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import SqliteTimesheetRepository


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("import", help="import a timesheet CSV")
    parser.add_argument("csv_path", type=Path)
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, config: Config) -> int:
    csv_path: Path = args.csv_path
    try:
        content = csv_path.read_text()
    except OSError as exc:
        raise ImporterError(f"cannot read {csv_path}: {exc}") from exc

    entries = TimesheetCsvImporter().parse(content)

    connection = connect_and_migrate(config.database_path)
    try:
        SqliteTimesheetRepository(connection).add_entries(entries)
        connection.commit()
    finally:
        connection.close()

    print(f"imported {len(entries)} timesheet entries")
    return 0
