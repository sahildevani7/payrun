from decimal import Decimal

import pytest

from payrun.deductions.code import DeductionCode
from payrun.deductions.flat import FlatDeductionCalculator
from payrun.deductions.percentage import PercentageDeductionCalculator
from payrun.deductions.registry import DeductionCalculator, DeductionRegistry
from payrun.errors import NotFoundError, ValidationError
from payrun.money import Money
from payrun.rate import Rate


def _flat() -> FlatDeductionCalculator:
    return FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))


def _percentage() -> PercentageDeductionCalculator:
    return PercentageDeductionCalculator(DeductionCode("UNION"), Rate(Decimal("0.02")))


def test_register_then_get_returns_the_same_calculator():
    registry = DeductionRegistry()
    calculator = _flat()
    registry.register(calculator)
    assert registry.get(calculator.code) is calculator


def test_get_missing_code_raises_not_found():
    registry = DeductionRegistry()
    with pytest.raises(NotFoundError):
        registry.get(DeductionCode("PARKING"))


def test_register_duplicate_code_raises_validation_error():
    registry = DeductionRegistry()
    registry.register(_flat())
    with pytest.raises(ValidationError):
        registry.register(_flat())


def test_codes_are_sorted():
    registry = DeductionRegistry()
    registry.register(_percentage())
    registry.register(_flat())
    assert [str(c) for c in registry.codes()] == ["PARKING", "UNION"]


def test_flat_calculator_satisfies_the_protocol():
    assert isinstance(_flat(), DeductionCalculator)


def test_percentage_calculator_satisfies_the_protocol():
    assert isinstance(_percentage(), DeductionCalculator)


def test_empty_registry_has_no_codes():
    assert DeductionRegistry().codes() == []


def test_registry_can_hold_more_than_two_calculators():
    registry = DeductionRegistry()
    registry.register(_flat())
    registry.register(_percentage())
    registry.register(FlatDeductionCalculator(DeductionCode("GYM"), Money(Decimal("15.00"), "USD")))
    assert [str(c) for c in registry.codes()] == ["GYM", "PARKING", "UNION"]
