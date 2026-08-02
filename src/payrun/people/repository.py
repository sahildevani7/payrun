"""Employee lookup, independent of storage backend.

`InMemoryEmployeeRepository` is the in-process implementation used by tests
and by callers that do not need persistence. `storage.repositories` provides
the SQLite-backed implementation of the same protocol.
"""

from __future__ import annotations

import datetime as dt
from typing import Protocol, runtime_checkable

from payrun.calendarx.frequency import Frequency
from payrun.errors import NotFoundError, ValidationError
from payrun.ids import EmployeeId
from payrun.people.employee import Employee


@runtime_checkable
class EmployeeRepository(Protocol):
    def add(self, employee: Employee) -> None: ...

    def get(self, employee_id: EmployeeId) -> Employee: ...

    def list_all(self) -> list[Employee]: ...

    def list_by_frequency(self, frequency: Frequency) -> list[Employee]: ...

    def list_active_on(self, day: dt.date) -> list[Employee]: ...


class InMemoryEmployeeRepository:
    def __init__(self) -> None:
        self._employees: dict[EmployeeId, Employee] = {}

    def add(self, employee: Employee) -> None:
        if employee.id in self._employees:
            raise ValidationError(f"employee {employee.id} already exists")
        self._employees[employee.id] = employee

    def get(self, employee_id: EmployeeId) -> Employee:
        try:
            return self._employees[employee_id]
        except KeyError:
            raise NotFoundError(f"no employee with id {employee_id}") from None

    def list_all(self) -> list[Employee]:
        return [self._employees[key] for key in sorted(self._employees, key=str)]

    def list_by_frequency(self, frequency: Frequency) -> list[Employee]:
        return [employee for employee in self.list_all() if employee.frequency is frequency]

    def list_active_on(self, day: dt.date) -> list[Employee]:
        return [
            employee for employee in self.list_all() if employee.employment.is_active_on(day)
        ]
