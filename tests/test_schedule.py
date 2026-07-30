import datetime as dt

import pytest

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.schedule import generate_schedule
from payrun.errors import ValidationError


def test_weekly_schedule_has_fifty_two_periods_of_seven_days():
    periods = generate_schedule(2026, Frequency.WEEKLY)
    assert len(periods) == 52
    assert all(p.day_span == 7 for p in periods)
    assert periods[0].start == dt.date(2026, 1, 1)
    assert periods[0].end == dt.date(2026, 1, 7)
    assert periods[1].start == dt.date(2026, 1, 8)


def test_biweekly_schedule_has_twenty_six_periods_of_fourteen_days():
    periods = generate_schedule(2026, Frequency.BIWEEKLY)
    assert len(periods) == 26
    assert all(p.day_span == 14 for p in periods)
    assert periods[0].start == dt.date(2026, 1, 1)


def test_semimonthly_schedule_splits_each_month_at_the_fifteenth():
    periods = generate_schedule(2026, Frequency.SEMIMONTHLY)
    assert len(periods) == 24
    january_first_half, january_second_half = periods[0], periods[1]
    assert january_first_half.start == dt.date(2026, 1, 1)
    assert january_first_half.end == dt.date(2026, 1, 15)
    assert january_second_half.start == dt.date(2026, 1, 16)
    assert january_second_half.end == dt.date(2026, 1, 31)


def test_semimonthly_schedule_handles_february_in_a_leap_year():
    periods = generate_schedule(2028, Frequency.SEMIMONTHLY)
    february_second_half = periods[3]
    assert february_second_half.end == dt.date(2028, 2, 29)


def test_monthly_schedule_has_twelve_periods_covering_full_months():
    periods = generate_schedule(2026, Frequency.MONTHLY)
    assert len(periods) == 12
    assert periods[0].start == dt.date(2026, 1, 1)
    assert periods[0].end == dt.date(2026, 1, 31)
    assert periods[1].start == dt.date(2026, 2, 1)
    assert periods[1].end == dt.date(2026, 2, 28)
    assert periods[-1].end == dt.date(2026, 12, 31)


def test_sequence_numbers_are_one_based_and_contiguous():
    periods = generate_schedule(2026, Frequency.MONTHLY)
    assert [p.sequence for p in periods] == list(range(1, 13))


def test_pay_date_lags_period_end_by_the_given_days():
    periods = generate_schedule(2026, Frequency.MONTHLY, pay_date_lag_days=3)
    assert periods[0].pay_date == periods[0].end + dt.timedelta(days=3)


def test_zero_lag_pays_on_the_period_end_date():
    periods = generate_schedule(2026, Frequency.WEEKLY, pay_date_lag_days=0)
    assert periods[0].pay_date == periods[0].end


def test_negative_lag_is_rejected():
    with pytest.raises(ValidationError):
        generate_schedule(2026, Frequency.MONTHLY, pay_date_lag_days=-1)


def test_periods_do_not_overlap_within_a_schedule():
    periods = generate_schedule(2026, Frequency.SEMIMONTHLY)
    for earlier, later in zip(periods, periods[1:], strict=False):
        assert earlier.end < later.start


def test_monthly_schedule_handles_february_in_a_leap_year():
    periods = generate_schedule(2028, Frequency.MONTHLY)
    assert periods[1].end == dt.date(2028, 2, 29)


def test_monthly_schedule_handles_february_in_a_non_leap_year():
    periods = generate_schedule(2026, Frequency.MONTHLY)
    assert periods[1].end == dt.date(2026, 2, 28)


def test_biweekly_schedule_last_period_end_date():
    periods = generate_schedule(2026, Frequency.BIWEEKLY)
    assert periods[-1].end == dt.date(2026, 1, 1) + dt.timedelta(days=26 * 14 - 1)


def test_weekly_schedule_sequence_is_contiguous():
    periods = generate_schedule(2026, Frequency.WEEKLY)
    assert [p.sequence for p in periods] == list(range(1, 53))


def test_semimonthly_first_half_is_always_fifteen_days():
    for month in range(1, 13):
        periods = generate_schedule(2026, Frequency.SEMIMONTHLY)
        first_half = periods[(month - 1) * 2]
        assert first_half.day_span == 15
