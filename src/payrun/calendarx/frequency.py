"""Pay frequencies supported by the base schedule generator."""

from __future__ import annotations

import enum


class Frequency(enum.Enum):
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    SEMIMONTHLY = "SEMIMONTHLY"
    MONTHLY = "MONTHLY"

    @property
    def periods_per_year(self) -> int:
        return _PERIODS_PER_YEAR[self]


_PERIODS_PER_YEAR: dict[Frequency, int] = {
    Frequency.WEEKLY: 52,
    Frequency.BIWEEKLY: 26,
    Frequency.SEMIMONTHLY: 24,
    Frequency.MONTHLY: 12,
}
