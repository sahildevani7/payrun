"""Compensation basis: what an employee is paid against.

Salaried compensation is an annual amount, divided across the pay
calendar's periods. Hourly compensation is a rate applied to hours worked.
Neither type computes a period's earnings itself — that is `earnings/`'s
job, reading whichever compensation type an employee carries.
"""

from __future__ import annotations

from dataclasses import dataclass

from payrun.errors import ValidationError
from payrun.money import Money


@dataclass(frozen=True, slots=True)
class SalariedCompensation:
    annual_amount: Money

    def __post_init__(self) -> None:
        if self.annual_amount.amount <= 0:
            raise ValidationError("annual_amount must be positive")


@dataclass(frozen=True, slots=True)
class HourlyCompensation:
    hourly_rate: Money

    def __post_init__(self) -> None:
        if self.hourly_rate.amount <= 0:
            raise ValidationError("hourly_rate must be positive")


Compensation = SalariedCompensation | HourlyCompensation
