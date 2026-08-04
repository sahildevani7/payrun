"""Pre-run validation: catch a bad run before any calculation happens."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from payrun.calendarx.period import PayPeriod
from payrun.errors import RunError
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.people.compensation import Compensation, HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee


def _compensation_currency(compensation: Compensation) -> str:
    if isinstance(compensation, SalariedCompensation):
        return compensation.annual_amount.currency
    return compensation.hourly_rate.currency


def validate_run(
    employees: Sequence[Employee],
    period: PayPeriod,
    hours_by_employee: Mapping[EmployeeId, Hours],
    currency: str | None = None,
) -> None:
    if not employees:
        raise RunError("a pay run requires at least one employee")

    seen: set[EmployeeId] = set()
    for employee in employees:
        if employee.id in seen:
            raise RunError(f"employee {employee.id} appears more than once in the run")
        seen.add(employee.id)

        if not employee.employment.is_active_on(period.end):
            raise RunError(f"employee {employee.id} is not active during {period}")

        is_hourly = isinstance(employee.compensation, HourlyCompensation)
        if is_hourly and employee.id not in hours_by_employee:
            raise RunError(f"missing timesheet hours for employee {employee.id}")

        if currency is not None and _compensation_currency(employee.compensation) != currency:
            raise RunError(
                f"employee {employee.id} is paid in a different currency than the run"
            )
