"""A deduction type identifier, e.g. `HEALTH` or `PARKING`."""

from __future__ import annotations

from dataclasses import dataclass

from payrun.errors import ValidationError


@dataclass(frozen=True, slots=True, order=True)
class DeductionCode:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValidationError("DeductionCode must be a non-blank string")
        object.__setattr__(self, "value", self.value.upper())

    def __str__(self) -> str:
        return self.value
