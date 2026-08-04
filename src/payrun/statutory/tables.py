"""Statutory parameter loading.

Rates, exemptions, and ceilings live in JSON files under `payrun/data/`, one
per plan year, and are loaded through this module only. No calculation
module reads the JSON directly or hardcodes a figure. Loading a plan year
with no parameter file raises `ParameterNotFoundError` rather than falling
back to the nearest year. Once loaded, a `StatutoryParameters` instance is
immutable and the loader caches it, so parsing happens at most once per
plan year.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
from pathlib import Path
from typing import Any

from payrun.errors import ParameterNotFoundError
from payrun.money import Money
from payrun.rate import Rate
from payrun.tax.brackets import TaxBracket, validate_ascending

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True, slots=True)
class PensionParameters:
    rate: Rate
    exemption_annual: Money
    ceiling_annual: Money


@dataclass(frozen=True, slots=True)
class InsuranceParameters:
    rate: Rate
    annual_maximum: Money


@dataclass(frozen=True, slots=True)
class EmployerParameters:
    pension_multiplier: Rate
    insurance_multiplier: Rate


@dataclass(frozen=True, slots=True)
class TaxParameters:
    basic_credit_annual: Money
    brackets: tuple[TaxBracket, ...]


@dataclass(frozen=True, slots=True)
class StatutoryParameters:
    plan_year: int
    currency: str
    pension: PensionParameters
    insurance: InsuranceParameters
    employer: EmployerParameters
    tax: TaxParameters


def _parse(plan_year: int, raw: dict[str, Any]) -> StatutoryParameters:
    currency = raw["currency"]
    pension_raw = raw["pension"]
    insurance_raw = raw["insurance"]
    employer_raw = raw["employer"]
    tax_raw = raw["tax"]
    brackets = tuple(
        TaxBracket(
            threshold=Money(Decimal(bracket["threshold"]), currency),
            rate=Rate(Decimal(bracket["rate"])),
        )
        for bracket in tax_raw["brackets"]
    )
    validate_ascending(brackets)
    return StatutoryParameters(
        plan_year=plan_year,
        currency=currency,
        pension=PensionParameters(
            rate=Rate(Decimal(pension_raw["rate"])),
            exemption_annual=Money(Decimal(pension_raw["exemption_annual"]), currency),
            ceiling_annual=Money(Decimal(pension_raw["ceiling_annual"]), currency),
        ),
        insurance=InsuranceParameters(
            rate=Rate(Decimal(insurance_raw["rate"])),
            annual_maximum=Money(Decimal(insurance_raw["annual_maximum"]), currency),
        ),
        employer=EmployerParameters(
            pension_multiplier=Rate(Decimal(employer_raw["pension_multiplier"])),
            insurance_multiplier=Rate(Decimal(employer_raw["insurance_multiplier"])),
        ),
        tax=TaxParameters(
            basic_credit_annual=Money(Decimal(tax_raw["basic_credit_annual"]), currency),
            brackets=brackets,
        ),
    )


@cache
def load_parameters(plan_year: int) -> StatutoryParameters:
    path = _DATA_DIR / f"parameters_{plan_year}.json"
    try:
        raw = json.loads(path.read_text())
    except OSError as exc:
        raise ParameterNotFoundError(plan_year, "parameters") from exc
    return _parse(plan_year, raw)


def available_plan_years() -> list[int]:
    """Every plan year with a parameter file, sorted ascending."""
    years = []
    for path in _DATA_DIR.glob("parameters_*.json"):
        year_part = path.stem.removeprefix("parameters_")
        if year_part.isdigit():
            years.append(int(year_part))
    return sorted(years)
