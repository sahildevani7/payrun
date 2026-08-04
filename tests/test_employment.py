import datetime as dt

import pytest

from payrun.errors import ValidationError
from payrun.people.employment import Employment, EmploymentStatus


def test_active_employment_needs_no_termination_date():
    employment = Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE)
    assert employment.termination_date is None


def test_active_employment_rejects_termination_date():
    with pytest.raises(ValidationError):
        Employment(
            hire_date=dt.date(2020, 1, 1),
            status=EmploymentStatus.ACTIVE,
            termination_date=dt.date(2026, 1, 1),
        )


def test_terminated_employment_requires_termination_date():
    with pytest.raises(ValidationError):
        Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.TERMINATED)


def test_terminated_employment_rejects_termination_before_hire():
    with pytest.raises(ValidationError):
        Employment(
            hire_date=dt.date(2020, 1, 1),
            status=EmploymentStatus.TERMINATED,
            termination_date=dt.date(2019, 1, 1),
        )


def test_is_active_on_before_hire_date_is_false():
    employment = Employment(hire_date=dt.date(2020, 6, 1), status=EmploymentStatus.ACTIVE)
    assert not employment.is_active_on(dt.date(2020, 5, 31))
    assert employment.is_active_on(dt.date(2020, 6, 1))


def test_is_active_on_after_termination_date_is_false():
    employment = Employment(
        hire_date=dt.date(2020, 1, 1),
        status=EmploymentStatus.TERMINATED,
        termination_date=dt.date(2026, 3, 15),
    )
    assert employment.is_active_on(dt.date(2026, 3, 15))
    assert not employment.is_active_on(dt.date(2026, 3, 16))


def test_termination_on_the_same_day_as_hire_is_allowed():
    employment = Employment(
        hire_date=dt.date(2026, 3, 15),
        status=EmploymentStatus.TERMINATED,
        termination_date=dt.date(2026, 3, 15),
    )
    assert employment.is_active_on(dt.date(2026, 3, 15))


def test_days_until_termination_counts_inclusive_days():
    employment = Employment(
        hire_date=dt.date(2020, 1, 1),
        status=EmploymentStatus.TERMINATED,
        termination_date=dt.date(2026, 3, 15),
    )
    assert employment.days_until_termination(dt.date(2026, 3, 15)) == 1
    assert employment.days_until_termination(dt.date(2026, 3, 1)) == 15
    assert employment.days_until_termination(dt.date(2026, 1, 1)) == 74


def test_days_until_termination_is_zero_after_the_termination_date():
    employment = Employment(
        hire_date=dt.date(2020, 1, 1),
        status=EmploymentStatus.TERMINATED,
        termination_date=dt.date(2026, 3, 15),
    )
    assert employment.days_until_termination(dt.date(2026, 3, 16)) == 0
    assert employment.days_until_termination(dt.date(2027, 1, 1)) == 0


def test_days_until_termination_on_the_termination_day_is_one():
    employment = Employment(
        hire_date=dt.date(2020, 1, 1),
        status=EmploymentStatus.TERMINATED,
        termination_date=dt.date(2026, 3, 15),
    )
    assert employment.days_until_termination(employment.termination_date) == 1


def test_days_until_termination_rejects_active_employment():
    employment = Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE)
    with pytest.raises(ValidationError):
        employment.days_until_termination(dt.date(2026, 3, 1))


def test_employment_equality():
    a = Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE)
    b = Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE)
    assert a == b


def test_employment_status_has_exactly_two_members():
    assert len(list(EmploymentStatus)) == 2
