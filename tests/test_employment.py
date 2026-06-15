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
