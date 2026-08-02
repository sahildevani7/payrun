"""`payrun run`: execute a pay run for every employee on the configured frequency.

Every employee added through the CLI carries a frequency of their own,
matching the domain model, but a single `run` invocation processes the
employees on the company's configured frequency for one period at a time —
the way a small business with one pay calendar actually runs payroll.
"""

from __future__ import annotations

import argparse
import datetime as dt

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.plan_calendar import PlanCalendar
from payrun.config import Config
from payrun.errors import ConfigurationError, RunError
from payrun.run.factory import build_engine
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import (
    SqliteEmployeeRepository,
    SqlitePayRunRepository,
    SqliteTimesheetRepository,
    load_ytd_store,
    save_ytd_store,
)


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("run", help="run payroll for a pay period")
    parser.add_argument("--period", required=True, help="ISO 8601 start date of the pay period")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, config: Config) -> int:
    try:
        period_start = dt.date.fromisoformat(args.period)
    except ValueError as exc:
        raise RunError(f"invalid --period: {exc}") from exc

    try:
        frequency = Frequency(config.frequency)
    except ValueError as exc:
        raise ConfigurationError(f"invalid frequency in config: {exc}") from exc

    calendar = PlanCalendar(config.plan_year, frequency)
    period = calendar.period_starting(period_start)

    connection = connect_and_migrate(config.database_path)
    try:
        employees = [
            employee
            for employee in SqliteEmployeeRepository(connection).list_all()
            if employee.frequency is frequency
        ]
        if not employees:
            raise RunError(f"no employees with frequency {frequency.value} to run")

        hours_by_employee = SqliteTimesheetRepository(connection).hours_for_period(period)
        ytd_store = load_ytd_store(connection, config.currency)
        engine = build_engine(
            currency=config.currency,
            plan_year=config.plan_year,
            frequency=frequency,
            ytd_store=ytd_store,
        )

        result = engine.run(employees, period, hours_by_employee)

        SqlitePayRunRepository(connection).save(result)
        save_ytd_store(connection, ytd_store)
        connection.commit()
    finally:
        connection.close()

    print(f"ran pay period {period} for {len(result.payslips)} employees")
    return 0
