"""Build a `PayRunEngine` from statutory parameters for one plan year and frequency.

Every caller that runs payroll — the CLI's `run` command, and any test that
needs a fully wired engine — needs the same handful of pieces assembled in
the same order: the earning and deduction registries, the pension and
insurance calculators, tax withholding, and the employer multipliers. This
module is that assembly, in one place, so nothing downstream repeats it.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.deductions.registry import DeductionCalculator, DeductionRegistry
from payrun.earnings.overtime import OvertimeEarningCalculator
from payrun.earnings.registry import EarningCalculator, default_registry
from payrun.hours import Hours
from payrun.rate import Rate
from payrun.run.engine import PayRunEngine
from payrun.run.ytd import YtdStore
from payrun.statutory.insurance import InsuranceCalculator
from payrun.statutory.pension import PensionCalculator
from payrun.statutory.tables import load_parameters
from payrun.tax.withholding import WithholdingCalculator

DEFAULT_WEEKLY_OVERTIME_THRESHOLD = Hours(Decimal("40"))
DEFAULT_OVERTIME_MULTIPLIER = Rate(Decimal("1.5"))


def build_engine(
    currency: str,
    plan_year: int,
    frequency: Frequency,
    ytd_store: YtdStore,
    weekly_overtime_threshold: Hours = DEFAULT_WEEKLY_OVERTIME_THRESHOLD,
    extra_earning_calculators: Sequence[EarningCalculator] = (),
    extra_deduction_calculators: Sequence[DeductionCalculator] = (),
) -> PayRunEngine:
    overtime_calculator = OvertimeEarningCalculator(
        weekly_threshold=weekly_overtime_threshold, multiplier=DEFAULT_OVERTIME_MULTIPLIER
    )
    earning_registry = default_registry(overtime_calculator)
    for earning_calculator in extra_earning_calculators:
        earning_registry.register(earning_calculator)

    deduction_registry = DeductionRegistry()
    for deduction_calculator in extra_deduction_calculators:
        deduction_registry.register(deduction_calculator)

    params = load_parameters(plan_year)

    return PayRunEngine(
        currency=currency,
        earning_registry=earning_registry,
        deduction_registry=deduction_registry,
        weekly_overtime_threshold=weekly_overtime_threshold,
        pension_calculator=PensionCalculator(params.pension, frequency),
        insurance_calculator=InsuranceCalculator(params.insurance),
        withholding_calculator=WithholdingCalculator(params.tax, frequency),
        employer_pension_multiplier=params.employer.pension_multiplier,
        employer_insurance_multiplier=params.employer.insurance_multiplier,
        ytd_store=ytd_store,
    )
