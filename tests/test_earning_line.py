from decimal import Decimal

import pytest

from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.errors import ValidationError
from payrun.hours import Hours
from payrun.money import Money


def test_holds_code_amount_and_hours():
    line = EarningLine(
        code=EarningCode("REGULAR"),
        amount=Money(Decimal("520.00"), "USD"),
        hours=Hours(Decimal("16")),
    )
    assert line.code == EarningCode("REGULAR")
    assert line.amount == Money(Decimal("520.00"), "USD")
    assert line.hours == Hours(Decimal("16"))


def test_hours_defaults_to_none_for_salaried_lines():
    line = EarningLine(code=EarningCode("REGULAR"), amount=Money(Decimal("3000.00"), "USD"))
    assert line.hours is None


def test_rejects_negative_amount():
    with pytest.raises(ValidationError):
        EarningLine(code=EarningCode("REGULAR"), amount=Money(Decimal("-1.00"), "USD"))


def test_zero_amount_is_allowed():
    line = EarningLine(code=EarningCode("OVERTIME"), amount=Money.zero("USD"))
    assert line.amount == Money.zero("USD")
