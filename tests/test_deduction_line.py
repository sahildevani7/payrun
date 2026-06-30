from decimal import Decimal

import pytest

from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.errors import ValidationError
from payrun.money import Money


def test_holds_code_and_amount():
    line = DeductionLine(code=DeductionCode("HEALTH"), amount=Money(Decimal("50.00"), "USD"))
    assert line.code == DeductionCode("HEALTH")
    assert line.amount == Money(Decimal("50.00"), "USD")


def test_rejects_negative_amount():
    with pytest.raises(ValidationError):
        DeductionLine(code=DeductionCode("HEALTH"), amount=Money(Decimal("-1.00"), "USD"))


def test_zero_amount_is_allowed():
    line = DeductionLine(code=DeductionCode("HEALTH"), amount=Money.zero("USD"))
    assert line.amount == Money.zero("USD")
