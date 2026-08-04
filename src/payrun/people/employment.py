"""Employment status: when someone started, and whether they have left."""

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass

from payrun.errors import ValidationError


class EmploymentStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"


@dataclass(frozen=True, slots=True)
class Employment:
    hire_date: dt.date
    status: EmploymentStatus
    termination_date: dt.date | None = None

    def __post_init__(self) -> None:
        if self.status is EmploymentStatus.TERMINATED:
            if self.termination_date is None:
                raise ValidationError("a terminated employment requires a termination_date")
            if self.termination_date < self.hire_date:
                raise ValidationError("termination_date must not precede hire_date")
        elif self.termination_date is not None:
            raise ValidationError("an active employment must not carry a termination_date")

    def is_active_on(self, day: dt.date) -> bool:
        if day < self.hire_date:
            return False
        if self.termination_date is not None and day > self.termination_date:
            return False
        return True

    def days_until_termination(self, day: dt.date) -> int:
        """Days from `day` through the termination date; 0 once past it."""
        if self.status is not EmploymentStatus.TERMINATED:
            raise ValidationError("days_until_termination requires a terminated employment")
        termination_date = self.termination_date
        if termination_date is None:
            raise ValidationError("days_until_termination requires a terminated employment")
        if day > termination_date:
            return 0
        return (termination_date - day).days + 1
