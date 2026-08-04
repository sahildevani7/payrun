"""`payrun register`: render the pay-run register for one period."""

from __future__ import annotations

import argparse

from payrun.cli.period import parse_period_start
from payrun.config import Config
from payrun.reporting.text import TextRenderer
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import SqlitePayRunRepository


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("register", help="render the pay-run register")
    parser.add_argument(
        "--period",
        required=True,
        help="ISO 8601 start date or sequence number of the pay period",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, config: Config) -> int:
    period_start = parse_period_start(args.period, config)

    connection = connect_and_migrate(config.database_path)
    try:
        result = SqlitePayRunRepository(connection).get_register(period_start)
    finally:
        connection.close()

    print(TextRenderer().render_register(result))
    return 0
