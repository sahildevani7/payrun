"""An injected table of holiday dates.

Nothing in this module knows today's date or any jurisdiction's actual
holiday calendar. The caller supplies the dates.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable


class HolidayCalendar:
    def __init__(self, dates: Iterable[dt.date]) -> None:
        self._dates = frozenset(dates)

    def is_holiday(self, day: dt.date) -> bool:
        return day in self._dates

    def between(self, start: dt.date, end: dt.date) -> list[dt.date]:
        return sorted(day for day in self._dates if start <= day <= end)

    def __len__(self) -> int:
        return len(self._dates)

    def __contains__(self, day: object) -> bool:
        return day in self._dates
