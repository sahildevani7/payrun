import datetime as dt

import pytest

from payrun.calendarx.period import PayPeriod
from payrun.errors import ValidationError


def test_day_span_is_inclusive():
    period = PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )
    assert period.day_span == 15


def test_contains_checks_inclusive_bounds():
    period = PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )
    assert period.contains(dt.date(2026, 3, 1))
    assert period.contains(dt.date(2026, 3, 15))
    assert not period.contains(dt.date(2026, 2, 28))
    assert not period.contains(dt.date(2026, 3, 16))


def test_rejects_end_before_start():
    with pytest.raises(ValidationError):
        PayPeriod(
            start=dt.date(2026, 3, 15),
            end=dt.date(2026, 3, 1),
            pay_date=dt.date(2026, 3, 20),
            sequence=1,
        )


def test_rejects_pay_date_before_end():
    with pytest.raises(ValidationError):
        PayPeriod(
            start=dt.date(2026, 3, 1),
            end=dt.date(2026, 3, 15),
            pay_date=dt.date(2026, 3, 10),
            sequence=1,
        )


def test_rejects_non_positive_sequence():
    with pytest.raises(ValidationError):
        PayPeriod(
            start=dt.date(2026, 3, 1),
            end=dt.date(2026, 3, 15),
            pay_date=dt.date(2026, 3, 20),
            sequence=0,
        )


def test_periods_order_by_start_date():
    earlier = PayPeriod(
        start=dt.date(2026, 1, 1),
        end=dt.date(2026, 1, 15),
        pay_date=dt.date(2026, 1, 20),
        sequence=1,
    )
    later = PayPeriod(
        start=dt.date(2026, 2, 1),
        end=dt.date(2026, 2, 15),
        pay_date=dt.date(2026, 2, 20),
        sequence=2,
    )
    assert earlier < later


def test_str_shows_the_span():
    period = PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )
    assert str(period) == "2026-03-01..2026-03-15"
