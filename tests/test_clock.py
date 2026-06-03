import datetime as dt

import pytest

from payrun.clock import Clock, FixedClock, SystemClock


def test_fixed_clock_returns_pinned_instant():
    clock = FixedClock(dt.datetime(2026, 3, 15, 9, 30))
    assert clock.now() == dt.datetime(2026, 3, 15, 9, 30)
    assert clock.today() == dt.date(2026, 3, 15)


def test_fixed_clock_at_constructs_midnight():
    clock = FixedClock.at(2026, 1, 1)
    assert clock.today() == dt.date(2026, 1, 1)
    assert clock.now() == dt.datetime(2026, 1, 1, 0, 0)


def test_fixed_clock_rejects_timezone_aware_datetime():
    with pytest.raises(ValueError):
        FixedClock(dt.datetime(2026, 1, 1, tzinfo=dt.UTC))


def test_fixed_clock_satisfies_clock_protocol():
    assert isinstance(FixedClock.at(2026, 1, 1), Clock)


def test_system_clock_satisfies_clock_protocol():
    assert isinstance(SystemClock(), Clock)


def test_system_clock_today_matches_now_date():
    clock = SystemClock()
    assert clock.today() == clock.now().date()
