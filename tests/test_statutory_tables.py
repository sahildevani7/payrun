from decimal import Decimal

import pytest

from payrun.errors import ParameterNotFoundError
from payrun.statutory.tables import available_plan_years, load_parameters


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


def test_available_plan_years_includes_every_shipped_year():
    assert {2025, 2026, 2027}.issubset(set(available_plan_years()))


def test_available_plan_years_is_sorted_ascending():
    years = available_plan_years()
    assert years == sorted(years)


def test_adjacent_plan_years_load_independently():
    year_2025 = load_parameters(2025)
    year_2027 = load_parameters(2027)
    assert year_2025.pension.exemption_annual.amount == Decimal("3300.00")
    assert year_2027.pension.exemption_annual.amount == Decimal("3500.00")
    assert year_2025 != year_2027


def test_each_shipped_plan_year_loads_without_error():
    for year in (2025, 2026, 2027):
        params = load_parameters(year)
        assert params.plan_year == year
