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


def test_frequency_constructs_from_its_value():
    assert Frequency("BIWEEKLY") is Frequency.BIWEEKLY


def test_frequency_has_exactly_four_members():
    assert len(list(Frequency)) == 4


def test_invalid_frequency_value_raises_value_error():
    with pytest.raises(ValueError):
        Frequency("YEARLY")
