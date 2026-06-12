import datetime as dt

from payrun.calendarx.holidays import HolidayCalendar


def test_is_holiday_true_for_injected_date():
    calendar = HolidayCalendar([dt.date(2026, 1, 1), dt.date(2026, 7, 4)])
    assert calendar.is_holiday(dt.date(2026, 1, 1))
    assert not calendar.is_holiday(dt.date(2026, 1, 2))


def test_between_returns_sorted_dates_in_range():
    calendar = HolidayCalendar([dt.date(2026, 7, 4), dt.date(2026, 1, 1), dt.date(2026, 12, 25)])
    assert calendar.between(dt.date(2026, 1, 1), dt.date(2026, 8, 1)) == [
        dt.date(2026, 1, 1),
        dt.date(2026, 7, 4),
    ]


def test_len_reports_distinct_holiday_count():
    calendar = HolidayCalendar([dt.date(2026, 1, 1), dt.date(2026, 1, 1)])
    assert len(calendar) == 1


def test_contains_operator():
    calendar = HolidayCalendar([dt.date(2026, 1, 1)])
    assert dt.date(2026, 1, 1) in calendar
    assert dt.date(2026, 1, 2) not in calendar


def test_empty_calendar_has_no_holidays():
    calendar = HolidayCalendar([])
    assert len(calendar) == 0
    assert not calendar.is_holiday(dt.date(2026, 1, 1))
