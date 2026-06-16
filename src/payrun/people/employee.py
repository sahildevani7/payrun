"""An employee: identity, pay frequency, employment status, and compensation."""

from __future__ import annotations

from dataclasses import dataclass

from payrun.calendarx.frequency import Frequency
from payrun.errors import ValidationError
from payrun.ids import EmployeeId
from payrun.people.compensation import Compensation
from payrun.people.employment import Employment


@dataclass(frozen=True, slots=True)
class Employee:
    id: EmployeeId
    first_name: str
    last_name: str
    frequency: Frequency
    employment: Employment
    compensation: Compensation

    def __post_init__(self) -> None:
        if not self.first_name.strip():
            raise ValidationError("first_name must be non-blank")
        if not self.last_name.strip():
            raise ValidationError("last_name must be non-blank")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
