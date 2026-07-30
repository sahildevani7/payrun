from decimal import Decimal

import pytest

from payrun.errors import ValidationError
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation


def test_salaried_compensation_holds_annual_amount():
    comp = SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    assert comp.annual_amount == Money(Decimal("78000.00"), "USD")


def test_salaried_compensation_rejects_zero_amount():
    with pytest.raises(ValidationError):
        SalariedCompensation(Money.zero("USD"))


def test_salaried_compensation_rejects_negative_amount():
    with pytest.raises(ValidationError):
        SalariedCompensation(Money(Decimal("-1.00"), "USD"))


def test_hourly_compensation_holds_rate():
    comp = HourlyCompensation(Money(Decimal("32.50"), "USD"))
    assert comp.hourly_rate == Money(Decimal("32.50"), "USD")


def test_hourly_compensation_rejects_zero_rate():
    with pytest.raises(ValidationError):
        HourlyCompensation(Money.zero("USD"))


def test_hourly_compensation_rejects_negative_rate():
    with pytest.raises(ValidationError):
        HourlyCompensation(Money(Decimal("-5.00"), "USD"))


def test_salaried_compensation_equality():
    a = SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    b = SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    assert a == b


def test_salaried_and_hourly_compensation_are_not_equal():
    salaried = SalariedCompensation(Money(Decimal("78000.00"), "USD"))
    hourly = HourlyCompensation(Money(Decimal("78000.00"), "USD"))
    assert salaried != hourly
