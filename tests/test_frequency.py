import pytest

from payrun.calendarx.frequency import Frequency


@pytest.mark.parametrize(
    "frequency, expected",
    [
        (Frequency.WEEKLY, 52),
        (Frequency.BIWEEKLY, 26),
        (Frequency.SEMIMONTHLY, 24),
        (Frequency.MONTHLY, 12),
    ],
)
def test_periods_per_year(frequency, expected):
    assert frequency.periods_per_year == expected


def test_frequency_values_are_stable_strings():
    assert Frequency.WEEKLY.value == "WEEKLY"
    assert Frequency.SEMIMONTHLY.value == "SEMIMONTHLY"
