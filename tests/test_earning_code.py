import pytest

from payrun.earnings.code import EarningCode
from payrun.errors import ValidationError


def test_normalizes_to_uppercase():
    assert EarningCode("regular").value == "REGULAR"


def test_rejects_blank_value():
    with pytest.raises(ValidationError):
        EarningCode("   ")


def test_equal_codes_are_equal_and_hashable():
    assert EarningCode("regular") == EarningCode("REGULAR")
    assert hash(EarningCode("regular")) == hash(EarningCode("REGULAR"))


def test_str_returns_normalized_value():
    assert str(EarningCode("overtime")) == "OVERTIME"


def test_codes_order_lexicographically():
    assert EarningCode("REGULAR") > EarningCode("OVERTIME")
