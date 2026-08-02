import datetime as dt

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.holidays import HolidayCalendar
from payrun.calendarx.plan_calendar import PlanCalendar
from payrun.errors import NotFoundError


def test_periods_matches_generate_schedule_count():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    assert len(calendar.periods()) == 12


def test_period_starting_finds_the_matching_period():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    period = calendar.period_starting(dt.date(2026, 3, 1))
    assert period.end == dt.date(2026, 3, 31)


def test_period_starting_raises_not_found_for_a_date_not_on_the_schedule():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    with pytest.raises(NotFoundError):
        calendar.period_starting(dt.date(2026, 3, 5))


def test_period_containing_finds_the_period_spanning_a_date():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    period = calendar.period_containing(dt.date(2026, 3, 17))
    assert period.start == dt.date(2026, 3, 1)


def test_period_containing_raises_not_found_outside_the_plan_year():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    with pytest.raises(NotFoundError):
        calendar.period_containing(dt.date(2027, 1, 15))


def test_sequence_of_matches_the_periods_position():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    assert calendar.sequence_of(dt.date(2026, 3, 1)) == 3


def test_working_days_in_uses_the_calendars_holidays():
    holidays = HolidayCalendar([dt.date(2026, 3, 2)])
    calendar = PlanCalendar(2026, Frequency.MONTHLY, holidays=holidays)
    period = calendar.period_starting(dt.date(2026, 3, 1))
    with_holiday = calendar.working_days_in(period)

    without_holiday = PlanCalendar(2026, Frequency.MONTHLY).working_days_in(period)
    assert with_holiday == without_holiday - 1


def test_default_holidays_is_empty():
    calendar = PlanCalendar(2026, Frequency.MONTHLY)
    assert len(calendar.holidays) == 0


def test_exposes_plan_year_and_frequency():
    calendar = PlanCalendar(2026, Frequency.BIWEEKLY)
    assert calendar.plan_year == 2026
    assert calendar.frequency is Frequency.BIWEEKLY


def test_custom_pay_date_lag_is_applied():
    calendar = PlanCalendar(2026, Frequency.MONTHLY, pay_date_lag_days=10)
    period = calendar.period_starting(dt.date(2026, 3, 1))
    assert period.pay_date == period.end + dt.timedelta(days=10)
