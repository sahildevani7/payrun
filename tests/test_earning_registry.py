import pytest

from payrun.earnings.overtime import OvertimeEarningCalculator, default_calculator
from payrun.earnings.registry import EarningCalculator, EarningRegistry
from payrun.earnings.regular import RegularEarningCalculator
from payrun.errors import NotFoundError, ValidationError


def test_register_then_get_returns_the_same_calculator():
    registry = EarningRegistry()
    calculator = RegularEarningCalculator()
    registry.register(calculator)
    assert registry.get(calculator.code) is calculator


def test_get_missing_code_raises_not_found():
    registry = EarningRegistry()
    with pytest.raises(NotFoundError):
        registry.get(RegularEarningCalculator().code)


def test_register_duplicate_code_raises_validation_error():
    registry = EarningRegistry()
    registry.register(RegularEarningCalculator())
    with pytest.raises(ValidationError):
        registry.register(RegularEarningCalculator())


def test_codes_are_sorted():
    registry = EarningRegistry()
    registry.register(default_calculator())
    registry.register(RegularEarningCalculator())
    assert [str(c) for c in registry.codes()] == ["OVERTIME", "REGULAR"]


def test_regular_calculator_satisfies_the_protocol():
    assert isinstance(RegularEarningCalculator(), EarningCalculator)


def test_overtime_calculator_satisfies_the_protocol():
    assert isinstance(default_calculator(), EarningCalculator)


def test_overtime_calculator_is_the_only_registered_implementation_type():
    assert isinstance(default_calculator(), OvertimeEarningCalculator)


def test_empty_registry_has_no_codes():
    assert EarningRegistry().codes() == []


def test_not_found_error_message_names_the_code():
    registry = EarningRegistry()
    with pytest.raises(NotFoundError, match="REGULAR"):
        registry.get(RegularEarningCalculator().code)
