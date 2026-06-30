import pytest

from payrun.deductions.code import DeductionCode
from payrun.errors import ValidationError


def test_normalizes_to_uppercase():
    assert DeductionCode("health").value == "HEALTH"


def test_rejects_blank_value():
    with pytest.raises(ValidationError):
        DeductionCode("")


def test_equal_codes_are_equal_and_hashable():
    assert DeductionCode("health") == DeductionCode("HEALTH")
    assert hash(DeductionCode("health")) == hash(DeductionCode("HEALTH"))
