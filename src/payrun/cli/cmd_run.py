"""`payrun run`: execute a pay run for every employee on the configured frequency.

Every employee added through the CLI carries a frequency of their own,
matching the domain model, but a single `run` invocation processes the
employees on the company's configured frequency for one period at a time —
the way a small business with one pay calendar actually runs payroll.
"""

from __future__ import annotations

import argparse
import datetime as dt
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.schedule import generate_schedule
from payrun.config import Config
from payrun.deductions.registry import DeductionRegistry
from payrun.earnings.overtime import default_calculator
from payrun.earnings.registry import EarningRegistry
from payrun.earnings.regular import RegularEarningCalculator
from payrun.errors import ConfigurationError, RunError
from payrun.hours import Hours
from payrun.run.engine import PayRunEngine
from payrun.statutory.insurance import InsuranceCalculator
from payrun.statutory.pension import PensionCalculator
from payrun.statutory.tables import load_parameters
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import (
    SqliteEmployeeRepository,
    SqlitePayRunRepository,
    SqliteTimesheetRepository,
    load_ytd_store,
    save_ytd_store,
)
from payrun.tax.withholding import WithholdingCalculator


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

    schedule = generate_schedule(config.plan_year, frequency)
    period = next((p for p in schedule if p.start == period_start), None)
    if period is None:
        raise RunError(
            f"no {frequency.value} period starts on {period_start} in plan year {config.plan_year}"
        )

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

        earning_registry = EarningRegistry()
        earning_registry.register(RegularEarningCalculator())
        earning_registry.register(default_calculator())

        params = load_parameters(config.plan_year)
        ytd_store = load_ytd_store(connection, config.currency)

        engine = PayRunEngine(
            currency=config.currency,
            earning_registry=earning_registry,
            deduction_registry=DeductionRegistry(),
            weekly_overtime_threshold=Hours(Decimal("40")),
            pension_calculator=PensionCalculator(params.pension, frequency),
            insurance_calculator=InsuranceCalculator(params.insurance),
            withholding_calculator=WithholdingCalculator(params.tax, frequency),
            employer_pension_multiplier=params.employer.pension_multiplier,
            employer_insurance_multiplier=params.employer.insurance_multiplier,
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
