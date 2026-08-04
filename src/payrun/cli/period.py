"""Shared parsing for the `--period` option across the period-taking commands.

A period may be named by its ISO 8601 start date or by its sequence number
on the configured frequency's schedule for the plan year. Both commands and
`run` use this so that `--period 3` and `--period 2026-03-01` mean the same
monthly period.
"""

from __future__ import annotations

import datetime as dt

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.plan_calendar import PlanCalendar
from payrun.config import Config
from payrun.errors import NotFoundError, RunError


def parse_period_start(value: str, config: Config) -> dt.date:
    if not value.isdigit():
        try:
            return dt.date.fromisoformat(value)
        except ValueError as exc:
            raise RunError(f"invalid --period: {exc}") from exc

    calendar = PlanCalendar(config.plan_year, Frequency(config.frequency))
    try:
        return calendar.period_by_sequence(int(value)).start
    except NotFoundError as exc:
        raise RunError(str(exc)) from exc
