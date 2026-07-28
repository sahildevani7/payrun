"""`payrun employees add`: register a new employee."""

from __future__ import annotations

import argparse
import datetime as dt
from decimal import Decimal, InvalidOperation

from payrun.calendarx.frequency import Frequency
from payrun.config import Config
from payrun.errors import ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.storage.engine import connect_and_migrate
from payrun.storage.repositories import SqliteEmployeeRepository


def add_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("employees", help="manage employees")
    employees_subparsers = parser.add_subparsers(dest="employees_command", required=True)

    add_parser = employees_subparsers.add_parser("add", help="add a new employee")
    add_parser.add_argument("--id", required=True)
    add_parser.add_argument("--first-name", required=True)
    add_parser.add_argument("--last-name", required=True)
    add_parser.add_argument("--frequency", required=True, choices=[f.value for f in Frequency])
    add_parser.add_argument("--hire-date", required=True, help="ISO 8601 date")
    add_parser.add_argument("--pay-type", required=True, choices=["SALARIED", "HOURLY"])
    add_parser.add_argument(
        "--amount", required=True, help="annual salary if SALARIED, hourly rate if HOURLY"
    )
    add_parser.set_defaults(handler=run)


def run(args: argparse.Namespace, config: Config) -> int:
    try:
        hire_date = dt.date.fromisoformat(args.hire_date)
        amount = Money(Decimal(args.amount), config.currency)
    except (ValueError, InvalidOperation) as exc:
        raise ValidationError(f"invalid employee argument: {exc}") from exc

    compensation = (
        SalariedCompensation(amount) if args.pay_type == "SALARIED" else HourlyCompensation(amount)
    )
    employee = Employee(
        id=EmployeeId(args.id),
        first_name=args.first_name,
        last_name=args.last_name,
        frequency=Frequency(args.frequency),
        employment=Employment(hire_date=hire_date, status=EmploymentStatus.ACTIVE),
        compensation=compensation,
    )

    connection = connect_and_migrate(config.database_path)
    try:
        SqliteEmployeeRepository(connection).add(employee)
        connection.commit()
    finally:
        connection.close()

    print(f"added employee {employee.id}")
    return 0
