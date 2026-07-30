from decimal import Decimal

import pytest

from payrun.rounding import RoundingMode, round_half_even, round_half_up, round_to_exponent


def test_round_half_up_rounds_midpoint_away_from_zero():
    assert round_half_up(Decimal("1.005"), 2) == Decimal("1.01")
    assert round_half_up(Decimal("1.015"), 2) == Decimal("1.02")


def test_round_half_even_rounds_midpoint_to_even_neighbor():
    assert round_half_even(Decimal("1.005"), 2) == Decimal("1.00")
    assert round_half_even(Decimal("1.015"), 2) == Decimal("1.02")


def test_round_to_exponent_zero_has_no_fraction():
    assert round_to_exponent(Decimal("4.6"), 0, RoundingMode.HALF_UP) == Decimal("5")


def test_round_to_exponent_preserves_already_exact_values():
    assert round_half_up(Decimal("3.00"), 2) == Decimal("3.00")


@pytest.mark.parametrize("mode", [RoundingMode.HALF_UP, RoundingMode.HALF_EVEN])
def test_round_to_exponent_negative_amounts(mode):
    result = round_to_exponent(Decimal("-1.005"), 2, mode)
    assert result <= Decimal("-1.00")


def test_round_half_even_picks_the_even_neighbor_above():
    assert round_half_even(Decimal("2.675"), 2) == Decimal("2.68")


def test_round_half_up_of_zero_is_zero():
    assert round_half_up(Decimal("0"), 2) == Decimal("0.00")


def test_rounding_mode_values_are_stable_strings():
    assert RoundingMode.HALF_UP.value == "HALF_UP"
    assert RoundingMode.HALF_EVEN.value == "HALF_EVEN"
