"""Generate a whole plan year's pay periods for a given frequency.

Each frequency divides the calendar year into equal-count periods:

- WEEKLY: 52 periods of 7 days, starting January 1.
- BIWEEKLY: 26 periods of 14 days, starting January 1.
- SEMIMONTHLY: 24 periods, the 1st through the 15th and the 16th through the
  last day of each month.
- MONTHLY: 12 periods, the first through the last day of each month.

The weekly and biweekly schedules cover 364 days from January 1 and do not
extend to December 31 in years where 365 or 366 does not divide evenly. This
is a base-repo simplification, not a general calendar reconciliation.
"""

from __future__ import annotations

import calendar
import datetime as dt

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.period import PayPeriod
from payrun.errors import ValidationError


def generate_schedule(
    plan_year: int, frequency: Frequency, pay_date_lag_days: int = 5
) -> list[PayPeriod]:
    if pay_date_lag_days < 0:
        raise ValidationError("pay_date_lag_days must be non-negative")

    if frequency is Frequency.WEEKLY:
        spans = _fixed_length_spans(plan_year, days=7, count=52)
    elif frequency is Frequency.BIWEEKLY:
        spans = _fixed_length_spans(plan_year, days=14, count=26)
    elif frequency is Frequency.SEMIMONTHLY:
        spans = _semimonthly_spans(plan_year)
    elif frequency is Frequency.MONTHLY:
        spans = _monthly_spans(plan_year)
    else:  # pragma: no cover - exhaustive over Frequency
        raise ValidationError(f"unsupported frequency {frequency!r}")

    lag = dt.timedelta(days=pay_date_lag_days)
    return [
        PayPeriod(start=start, end=end, pay_date=end + lag, sequence=sequence)
        for sequence, (start, end) in enumerate(spans, start=1)
    ]


def _fixed_length_spans(
    plan_year: int, days: int, count: int
) -> list[tuple[dt.date, dt.date]]:
    anchor = dt.date(plan_year, 1, 1)
    spans = []
    for i in range(count):
        start = anchor + dt.timedelta(days=days * i)
        end = start + dt.timedelta(days=days - 1)
        spans.append((start, end))
    return spans


def _semimonthly_spans(plan_year: int) -> list[tuple[dt.date, dt.date]]:
    spans = []
    for month in range(1, 13):
        last_day = calendar.monthrange(plan_year, month)[1]
        spans.append((dt.date(plan_year, month, 1), dt.date(plan_year, month, 15)))
        spans.append((dt.date(plan_year, month, 16), dt.date(plan_year, month, last_day)))
    return spans


def _monthly_spans(plan_year: int) -> list[tuple[dt.date, dt.date]]:
    spans = []
    for month in range(1, 13):
        last_day = calendar.monthrange(plan_year, month)[1]
        spans.append((dt.date(plan_year, month, 1), dt.date(plan_year, month, last_day)))
    return spans
