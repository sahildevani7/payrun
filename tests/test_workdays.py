import datetime as dt

from payrun.calendarx.holidays import HolidayCalendar
from payrun.calendarx.period import PayPeriod
from payrun.calendarx.workdays import is_workday, working_days


def test_is_workday_excludes_weekends():
    holidays = HolidayCalendar([])
    assert is_workday(dt.date(2026, 3, 2), holidays)  # Monday
    assert not is_workday(dt.date(2026, 3, 7), holidays)  # Saturday
    assert not is_workday(dt.date(2026, 3, 8), holidays)  # Sunday


def test_is_workday_excludes_holidays():
    holidays = HolidayCalendar([dt.date(2026, 3, 2)])
    assert not is_workday(dt.date(2026, 3, 2), holidays)


def test_working_days_counts_weekdays_in_a_full_week():
    period = PayPeriod(
        start=dt.date(2026, 3, 2),
        end=dt.date(2026, 3, 8),
        pay_date=dt.date(2026, 3, 10),
        sequence=1,
    )
    assert working_days(period, HolidayCalendar([])) == 5


def test_working_days_subtracts_holiday_within_period():
    period = PayPeriod(
        start=dt.date(2026, 3, 2),
        end=dt.date(2026, 3, 8),
        pay_date=dt.date(2026, 3, 10),
        sequence=1,
    )
    holidays = HolidayCalendar([dt.date(2026, 3, 4)])
    assert working_days(period, holidays) == 4


def test_working_days_for_single_day_period():
    period = PayPeriod(
        start=dt.date(2026, 3, 2),
        end=dt.date(2026, 3, 2),
        pay_date=dt.date(2026, 3, 5),
        sequence=1,
    )
    assert working_days(period, HolidayCalendar([])) == 1


def test_working_days_zero_when_period_is_entirely_a_weekend():
    period = PayPeriod(
        start=dt.date(2026, 3, 7),
        end=dt.date(2026, 3, 8),
        pay_date=dt.date(2026, 3, 10),
        sequence=1,
    )
    assert working_days(period, HolidayCalendar([])) == 0
