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


def test_loads_tax_parameters_for_known_plan_year():
    params = load_parameters(2026)
    assert params.tax.basic_credit_annual.amount == Decimal("1000.00")
    assert len(params.tax.brackets) == 4
    assert params.tax.brackets[0].threshold.amount == Decimal("0.00")
    assert params.tax.brackets[0].rate.value == Decimal("0.10")


def test_currency_is_shared_across_all_money_fields():
    params = load_parameters(2026)
    assert params.pension.exemption_annual.currency == params.currency
    assert params.insurance.annual_maximum.currency == params.currency


def test_unknown_plan_year_raises_parameter_not_found():
    with pytest.raises(ParameterNotFoundError):
        load_parameters(1999)


def test_loading_the_same_plan_year_twice_returns_equal_parameters():
    assert load_parameters(2026) == load_parameters(2026)


def test_loading_the_same_plan_year_twice_returns_the_same_object():
    assert load_parameters(2026) is load_parameters(2026)


def test_parameter_not_found_error_names_the_plan_year():
    with pytest.raises(ParameterNotFoundError, match="1999"):
        load_parameters(1999)


def test_tax_brackets_are_ordered_ascending_by_threshold():
    params = load_parameters(2026)
    thresholds = [bracket.threshold.amount for bracket in params.tax.brackets]
    assert thresholds == sorted(thresholds)
