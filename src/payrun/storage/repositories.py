"""SQLite-backed implementation of `people.repository.EmployeeRepository`."""

from __future__ import annotations

import datetime as dt
import sqlite3
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.errors import NotFoundError, ValidationError
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import Compensation, HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus

_INSERT_SQL = """
INSERT INTO employees (
    id, first_name, last_name, frequency, hire_date, status,
    termination_date, compensation_type, compensation_amount, currency
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_SELECT_ALL_SQL = "SELECT * FROM employees ORDER BY id"
_SELECT_ONE_SQL = "SELECT * FROM employees WHERE id = ?"


def _compensation_type(compensation: Compensation) -> str:
    if isinstance(compensation, SalariedCompensation):
        return "SALARIED"
    return "HOURLY"


def _compensation_amount(compensation: Compensation) -> Money:
    if isinstance(compensation, SalariedCompensation):
        return compensation.annual_amount
    return compensation.hourly_rate


def _row_from_employee(employee: Employee) -> tuple[object, ...]:
    amount = _compensation_amount(employee.compensation)
    return (
        str(employee.id),
        employee.first_name,
        employee.last_name,
        employee.frequency.value,
        employee.employment.hire_date.isoformat(),
        employee.employment.status.value,
        employee.employment.termination_date.isoformat()
        if employee.employment.termination_date
        else None,
        _compensation_type(employee.compensation),
        str(amount.amount),
        amount.currency,
    )


def _employee_from_row(row: sqlite3.Row) -> Employee:
    termination_date = (
        dt.date.fromisoformat(row["termination_date"]) if row["termination_date"] else None
    )
    employment = Employment(
        hire_date=dt.date.fromisoformat(row["hire_date"]),
        status=EmploymentStatus(row["status"]),
        termination_date=termination_date,
    )
    amount = Money(Decimal(row["compensation_amount"]), row["currency"])
    compensation: Compensation = (
        SalariedCompensation(amount)
        if row["compensation_type"] == "SALARIED"
        else HourlyCompensation(amount)
    )
    return Employee(
        id=EmployeeId(row["id"]),
        first_name=row["first_name"],
        last_name=row["last_name"],
        frequency=Frequency(row["frequency"]),
        employment=employment,
        compensation=compensation,
    )


class SqliteEmployeeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, employee: Employee) -> None:
        try:
            self._connection.execute(_INSERT_SQL, _row_from_employee(employee))
        except sqlite3.IntegrityError as exc:
            raise ValidationError(f"employee {employee.id} already exists") from exc

    def get(self, employee_id: EmployeeId) -> Employee:
        row = self._connection.execute(_SELECT_ONE_SQL, (str(employee_id),)).fetchone()
        if row is None:
            raise NotFoundError(f"no employee with id {employee_id}")
        return _employee_from_row(row)

    def list_all(self) -> list[Employee]:
        rows = self._connection.execute(_SELECT_ALL_SQL).fetchall()
        return [_employee_from_row(row) for row in rows]
