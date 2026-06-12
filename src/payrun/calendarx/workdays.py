"""Working-day counts over a pay period, net of weekends and holidays."""

from __future__ import annotations

import datetime as dt

from payrun.calendarx.holidays import HolidayCalendar
from payrun.calendarx.period import PayPeriod

_WEEKEND = frozenset({5, 6})  # Saturday, Sunday


def is_workday(day: dt.date, holidays: HolidayCalendar) -> bool:
    return day.weekday() not in _WEEKEND and not holidays.is_holiday(day)


def working_days(period: PayPeriod, holidays: HolidayCalendar) -> int:
    count = 0
    day = period.start
    one_day = dt.timedelta(days=1)
    while day <= period.end:
        if is_workday(day, holidays):
            count += 1
        day += one_day
    return count
