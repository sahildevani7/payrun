"""A plan year's schedule bound to one frequency, with holiday-aware lookups.

`generate_schedule` produces a bare list of periods. `PlanCalendar` is what
callers actually hold onto: it keeps the schedule alongside the holiday
table it was built with, and answers the two questions everything else
needs — which period starts on this date, and which period contains this
date — without recomputing the schedule each time.
"""

from __future__ import annotations

import datetime as dt

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.holidays import HolidayCalendar
from payrun.calendarx.period import PayPeriod
from payrun.calendarx.schedule import generate_schedule
from payrun.calendarx.workdays import working_days
from payrun.errors import NotFoundError


class PlanCalendar:
    def __init__(
        self,
        plan_year: int,
        frequency: Frequency,
        holidays: HolidayCalendar | None = None,
        pay_date_lag_days: int = 5,
    ) -> None:
        self._plan_year = plan_year
        self._frequency = frequency
        self._holidays = holidays if holidays is not None else HolidayCalendar([])
        self._periods = tuple(generate_schedule(plan_year, frequency, pay_date_lag_days))

    @property
    def plan_year(self) -> int:
        return self._plan_year

    @property
    def frequency(self) -> Frequency:
        return self._frequency

    @property
    def holidays(self) -> HolidayCalendar:
        return self._holidays

    def periods(self) -> tuple[PayPeriod, ...]:
        return self._periods

    def period_starting(self, start: dt.date) -> PayPeriod:
        for period in self._periods:
            if period.start == start:
                return period
        raise NotFoundError(
            f"no {self._frequency.value} period starts on {start} in plan year {self._plan_year}"
        )

    def period_by_sequence(self, sequence: int) -> PayPeriod:
        for period in self._periods:
            if period.sequence == sequence:
                return period
        raise NotFoundError(
            f"no {self._frequency.value} period with sequence {sequence} "
            f"in plan year {self._plan_year}"
        )

    def period_containing(self, day: dt.date) -> PayPeriod:
        for period in self._periods:
            if period.contains(day):
                return period
        raise NotFoundError(
            f"no {self._frequency.value} period in plan year {self._plan_year} contains {day}"
        )

    def working_days_in(self, period: PayPeriod) -> int:
        return working_days(period, self._holidays)

    def sequence_of(self, start: dt.date) -> int:
        return self.period_starting(start).sequence
