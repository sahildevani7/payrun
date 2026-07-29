"""`payrun register`: render the pay-run register for one period."""

from __future__ import annotations

import argparse
import datetime as dt

from payrun.config import Config
from payrun.errors import RunError
from payrun.reporting.text import TextRenderer
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import SqlitePayRunRepository


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("register", help="render the pay-run register")
    parser.add_argument("--period", required=True, help="ISO 8601 start date of the pay period")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, config: Config) -> int:
    try:
        period_start = dt.date.fromisoformat(args.period)
    except ValueError as exc:
        raise RunError(f"invalid --period: {exc}") from exc

    connection = connect_and_migrate(config.database_path)
    try:
        result = SqlitePayRunRepository(connection).get_register(period_start)
    finally:
        connection.close()

    print(TextRenderer().render_register(result))
    return 0
