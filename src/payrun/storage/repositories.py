"""SQLite-backed repositories for employees, timesheets, pay runs, and YTD totals."""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import NotFoundError, ValidationError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.importers.base import TimesheetEntry, aggregate_hours
from payrun.money import Money
from payrun.people.compensation import Compensation, HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.run.result import PayRunResult, PaySlip
from payrun.run.ytd import YtdAccumulator, YtdStore

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


class SqliteTimesheetRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add_entries(self, entries: Sequence[TimesheetEntry]) -> None:
        for entry in entries:
            self._connection.execute(
                "INSERT OR REPLACE INTO timesheet_entries (employee_id, work_date, hours) "
                "VALUES (?, ?, ?)",
                (str(entry.employee_id), entry.work_date.isoformat(), str(entry.hours.value)),
            )

    def hours_for_period(self, period: PayPeriod) -> dict[EmployeeId, Hours]:
        rows = self._connection.execute(
            "SELECT employee_id, work_date, hours FROM timesheet_entries "
            "WHERE work_date BETWEEN ? AND ?",
            (period.start.isoformat(), period.end.isoformat()),
        ).fetchall()
        entries = [
            TimesheetEntry(
                EmployeeId(row["employee_id"]),
                dt.date.fromisoformat(row["work_date"]),
                Hours(Decimal(row["hours"])),
            )
            for row in rows
        ]
        return aggregate_hours(entries)


def _earning_line_to_dict(line: EarningLine) -> dict[str, Any]:
    return {
        "code": str(line.code),
        "amount": str(line.amount.amount),
        "currency": line.amount.currency,
        "hours": str(line.hours.value) if line.hours is not None else None,
    }


def _earning_line_from_dict(data: dict[str, Any]) -> EarningLine:
    hours = Hours(Decimal(data["hours"])) if data["hours"] is not None else None
    amount = Money(Decimal(data["amount"]), data["currency"])
    return EarningLine(code=EarningCode(data["code"]), amount=amount, hours=hours)


def _deduction_line_to_dict(line: DeductionLine) -> dict[str, Any]:
    return {
        "code": str(line.code),
        "amount": str(line.amount.amount),
        "currency": line.amount.currency,
    }


def _deduction_line_from_dict(data: dict[str, Any]) -> DeductionLine:
    amount = Money(Decimal(data["amount"]), data["currency"])
    return DeductionLine(code=DeductionCode(data["code"]), amount=amount)


def _payslip_from_row(row: sqlite3.Row) -> PaySlip:
    currency = row["currency"]
    period = PayPeriod(
        start=dt.date.fromisoformat(row["period_start"]),
        end=dt.date.fromisoformat(row["period_end"]),
        pay_date=dt.date.fromisoformat(row["pay_date"]),
        sequence=row["sequence"],
    )
    return PaySlip(
        employee_id=EmployeeId(row["employee_id"]),
        period=period,
        earnings=tuple(_earning_line_from_dict(d) for d in json.loads(row["earnings_json"])),
        deductions=tuple(_deduction_line_from_dict(d) for d in json.loads(row["deductions_json"])),
        employer_contributions=tuple(
            _deduction_line_from_dict(d) for d in json.loads(row["employer_contributions_json"])
        ),
        gross=Money(Decimal(row["gross"]), currency),
        net=Money(Decimal(row["net"]), currency),
    )


class SqlitePayRunRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, result: PayRunResult) -> None:
        period = result.period
        for payslip in result.payslips:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO payslips (
                    period_start, employee_id, period_end, pay_date, sequence,
                    gross, net, currency, earnings_json, deductions_json,
                    employer_contributions_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    period.start.isoformat(),
                    str(payslip.employee_id),
                    period.end.isoformat(),
                    period.pay_date.isoformat(),
                    period.sequence,
                    str(payslip.gross.amount),
                    str(payslip.net.amount),
                    payslip.gross.currency,
                    json.dumps([_earning_line_to_dict(line) for line in payslip.earnings]),
                    json.dumps([_deduction_line_to_dict(line) for line in payslip.deductions]),
                    json.dumps(
                        [_deduction_line_to_dict(line) for line in payslip.employer_contributions]
                    ),
                ),
            )

    def get_payslip(self, employee_id: EmployeeId, period_start: dt.date) -> PaySlip:
        row = self._connection.execute(
            "SELECT * FROM payslips WHERE period_start = ? AND employee_id = ?",
            (period_start.isoformat(), str(employee_id)),
        ).fetchone()
        if row is None:
            raise NotFoundError(
                f"no payslip for employee {employee_id} in the period starting {period_start}"
            )
        return _payslip_from_row(row)

    def get_register(self, period_start: dt.date) -> PayRunResult:
        rows = self._connection.execute(
            "SELECT * FROM payslips WHERE period_start = ? ORDER BY employee_id",
            (period_start.isoformat(),),
        ).fetchall()
        if not rows:
            raise NotFoundError(f"no pay run recorded for the period starting {period_start}")
        payslips = tuple(_payslip_from_row(row) for row in rows)
        period = PayPeriod(
            start=period_start,
            end=dt.date.fromisoformat(rows[0]["period_end"]),
            pay_date=dt.date.fromisoformat(rows[0]["pay_date"]),
            sequence=rows[0]["sequence"],
        )
        return PayRunResult(period=period, payslips=payslips)


def load_ytd_store(connection: sqlite3.Connection, currency: str) -> YtdStore:
    store = YtdStore(currency)
    rows = connection.execute("SELECT * FROM ytd_accumulators").fetchall()
    for row in rows:
        accumulator = YtdAccumulator(
            gross=Money(Decimal(row["gross"]), currency),
            pension=Money(Decimal(row["pension"]), currency),
            insurance=Money(Decimal(row["insurance"]), currency),
            tax=Money(Decimal(row["tax"]), currency),
        )
        store.set(EmployeeId(row["employee_id"]), accumulator)
    return store


def save_ytd_store(connection: sqlite3.Connection, store: YtdStore) -> None:
    for employee_id, accumulator in store.items():
        connection.execute(
            """
            INSERT OR REPLACE INTO ytd_accumulators (
                employee_id, currency, gross, pension, insurance, tax
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(employee_id),
                accumulator.gross.currency,
                str(accumulator.gross.amount),
                str(accumulator.pension.amount),
                str(accumulator.insurance.amount),
                str(accumulator.tax.amount),
            ),
        )
