from decimal import Decimal

import pytest

from payrun.errors import ParameterNotFoundError
from payrun.statutory.tables import load_parameters


def test_loads_pension_parameters_for_known_plan_year():
    params = load_parameters(2026)
    assert params.pension.rate.value == Decimal("0.0525")
    assert params.pension.exemption_annual.amount == Decimal("3400.00")
    assert params.pension.ceiling_annual.amount == Decimal("71000.00")


def test_loads_insurance_parameters_for_known_plan_year():
    params = load_parameters(2026)
    assert params.insurance.rate.value == Decimal("0.0175")
    assert params.insurance.annual_maximum.amount == Decimal("950.00")


def test_loads_employer_parameters_for_known_plan_year():
    params = load_parameters(2026)
    assert params.employer.pension_multiplier.value == Decimal("1.0")
    assert params.employer.insurance_multiplier.value == Decimal("1.4")


def test_currency_is_shared_across_all_money_fields():
    params = load_parameters(2026)
    assert params.pension.exemption_annual.currency == params.currency
    assert params.insurance.annual_maximum.currency == params.currency


def test_unknown_plan_year_raises_parameter_not_found():
    with pytest.raises(ParameterNotFoundError):
        load_parameters(1999)


def test_loading_the_same_plan_year_twice_returns_equal_parameters():
    assert load_parameters(2026) == load_parameters(2026)
