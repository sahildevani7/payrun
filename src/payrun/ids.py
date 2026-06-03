"""Typed identifiers.

Plain strings are never passed where an identifier is expected. Each id type
validates its value once at construction; after that it is assumed valid.
"""

from __future__ import annotations

from dataclasses import dataclass

from payrun.errors import ValidationError


def _validate_nonblank(kind: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{kind} must be a non-blank string")
    return value


@dataclass(frozen=True, slots=True, order=True)
class EmployeeId:
    value: str

    def __post_init__(self) -> None:
        _validate_nonblank("EmployeeId", self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class PeriodId:
    value: str

    def __post_init__(self) -> None:
        _validate_nonblank("PeriodId", self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class PayRunId:
    value: str

    def __post_init__(self) -> None:
        _validate_nonblank("PayRunId", self.value)

    def __str__(self) -> str:
        return self.value
