"""The `payrun` CLI entry point: argument parsing and dispatch.

Every subcommand module exposes `add_subparser(subparsers)`, which wires a
`handler(args, config) -> int` as the subparser's default. `main` loads
config once, dispatches to that handler, and turns any `PayrunError` into a
message on stderr and exit code 1. Argument-parsing failures exit 2, via
argparse's own default behavior.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from payrun.cli import cmd_employees, cmd_import, cmd_payslip, cmd_register, cmd_run
from payrun.config import Config, load_config
from payrun.errors import PayrunError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="payrun")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("payrun.config.json"),
        help="path to the JSON configuration file",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    cmd_employees.add_subparser(subparsers)
    cmd_import.add_subparser(subparsers)
    cmd_run.add_subparser(subparsers)
    cmd_payslip.add_subparser(subparsers)
    cmd_register.add_subparser(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config: Config = load_config(args.config)
        return int(args.handler(args, config))
    except PayrunError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
