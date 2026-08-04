"""`payrun employees`: add, list, and show employees."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
from decimal import Decimal, InvalidOperation

from payrun.calendarx.frequency import Frequency
from payrun.cli.formatting import format_table
from payrun.config import Config
from payrun.errors import ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import Compensation, HourlyCompensation, SalariedCompensation
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
    add_parser.set_defaults(handler=run_add)

    list_parser = employees_subparsers.add_parser("list", help="list every employee")
    list_parser.set_defaults(handler=run_list)

    show_parser = employees_subparsers.add_parser("show", help="show one employee's details")
    show_parser.add_argument("--id", required=True)
    show_parser.set_defaults(handler=run_show)

    terminate_parser = employees_subparsers.add_parser("terminate", help="terminate an employee")
    terminate_parser.add_argument("--id", required=True)
    terminate_parser.add_argument("--termination-date", required=True, help="ISO 8601 date")
    terminate_parser.set_defaults(handler=run_terminate)


def _compensation_summary(compensation: Compensation) -> tuple[str, str]:
    if isinstance(compensation, SalariedCompensation):
        return "SALARIED", str(compensation.annual_amount)
    return "HOURLY", str(compensation.hourly_rate)


def run_add(args: argparse.Namespace, config: Config) -> int:
    try:
        hire_date = dt.date.fromisoformat(args.hire_date)
        amount = Money(Decimal(args.amount), config.currency)
    except (ValueError, InvalidOperation) as exc:
        raise ValidationError(f"invalid employee argument: {exc}") from exc

    compensation: Compensation = (
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


def run_list(args: argparse.Namespace, config: Config) -> int:
    connection = connect_and_migrate(config.database_path)
    try:
        employees = SqliteEmployeeRepository(connection).list_all()
    finally:
        connection.close()

    rows = []
    for employee in employees:
        pay_type, amount = _compensation_summary(employee.compensation)
        rows.append(
            [
                str(employee.id),
                employee.full_name,
                employee.frequency.value,
                employee.employment.status.value,
                pay_type,
                amount,
            ]
        )
    headers = ["ID", "Name", "Frequency", "Status", "Pay Type", "Amount"]
    print(format_table(headers, rows))
    return 0


def run_show(args: argparse.Namespace, config: Config) -> int:
    connection = connect_and_migrate(config.database_path)
    try:
        employee = SqliteEmployeeRepository(connection).get(EmployeeId(args.id))
    finally:
        connection.close()

    pay_type, amount = _compensation_summary(employee.compensation)
    print(f"Employee: {employee.id}")
    print(f"Name: {employee.full_name}")
    print(f"Frequency: {employee.frequency.value}")
    print(f"Hire date: {employee.employment.hire_date.isoformat()}")
    print(f"Status: {employee.employment.status.value}")
    if employee.employment.termination_date is not None:
        print(f"Termination date: {employee.employment.termination_date.isoformat()}")
    print(f"Pay type: {pay_type}")
    print(f"Amount: {amount}")
    return 0


def run_terminate(args: argparse.Namespace, config: Config) -> int:
    try:
        termination_date = dt.date.fromisoformat(args.termination_date)
    except ValueError as exc:
        raise ValidationError(f"invalid --termination-date: {exc}") from exc

    connection = connect_and_migrate(config.database_path)
    try:
        repository = SqliteEmployeeRepository(connection)
        employee = repository.get(EmployeeId(args.id))
        terminated = dataclasses.replace(
            employee,
            employment=Employment(
                hire_date=employee.employment.hire_date,
                status=EmploymentStatus.TERMINATED,
                termination_date=termination_date,
            ),
        )
        repository.update(terminated)
        connection.commit()
    finally:
        connection.close()

    print(f"terminated employee {args.id} effective {termination_date.isoformat()}")
    return 0
