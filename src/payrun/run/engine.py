"""Pay-run orchestration: earnings, deductions, statutory withholding, net pay.

For each employee this brings together the earning registry, the pension
and insurance calculators, tax withholding, and any voluntary deductions,
in that order, and records the results into the year-to-date store.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.line import DeductionLine
from payrun.deductions.registry import DeductionRegistry
from payrun.earnings.code import EarningCode
from payrun.earnings.line import EarningLine
from payrun.earnings.registry import EarningRegistry
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation
from payrun.people.employee import Employee
from payrun.rate import Rate
from payrun.run.result import PayRunResult, PaySlip
from payrun.run.validation import validate_run
from payrun.run.ytd import YtdStore
from payrun.statutory.employer import employer_share
from payrun.statutory.insurance import InsuranceCalculator
from payrun.statutory.pension import PensionCalculator
from payrun.tax.withholding import WithholdingCalculator

REGULAR = EarningCode("REGULAR")
OVERTIME = EarningCode("OVERTIME")
PENSION = DeductionCode("PENSION")
INSURANCE = DeductionCode("INSURANCE")
TAX = DeductionCode("TAX")


def _sum_money(currency: str, amounts: Iterable[Money]) -> Money:
    total = Money.zero(currency)
    for amount in amounts:
        total = total + amount
    return total


class PayRunEngine:
    def __init__(
        self,
        currency: str,
        earning_registry: EarningRegistry,
        deduction_registry: DeductionRegistry,
        weekly_overtime_threshold: Hours,
        pension_calculator: PensionCalculator,
        insurance_calculator: InsuranceCalculator,
        withholding_calculator: WithholdingCalculator,
        employer_pension_multiplier: Rate,
        employer_insurance_multiplier: Rate,
        ytd_store: YtdStore,
    ) -> None:
        self._currency = currency
        self._earning_registry = earning_registry
        self._deduction_registry = deduction_registry
        self._weekly_overtime_threshold = weekly_overtime_threshold
        self._pension_calculator = pension_calculator
        self._insurance_calculator = insurance_calculator
        self._withholding_calculator = withholding_calculator
        self._employer_pension_multiplier = employer_pension_multiplier
        self._employer_insurance_multiplier = employer_insurance_multiplier
        self._ytd_store = ytd_store

    @property
    def ytd_store(self) -> YtdStore:
        return self._ytd_store

    def run(
        self,
        employees: Sequence[Employee],
        period: PayPeriod,
        hours_by_employee: Mapping[EmployeeId, Hours],
        voluntary_codes_by_employee: Mapping[EmployeeId, Sequence[DeductionCode]] | None = None,
    ) -> PayRunResult:
        validate_run(employees, period, hours_by_employee, currency=self._currency)
        codes_by_employee = voluntary_codes_by_employee or {}

        payslips = [
            self._run_one(employee, period, hours_by_employee, codes_by_employee)
            for employee in sorted(employees, key=lambda e: str(e.id))
        ]
        return PayRunResult(period=period, payslips=tuple(payslips))

    def _run_one(
        self,
        employee: Employee,
        period: PayPeriod,
        hours_by_employee: Mapping[EmployeeId, Hours],
        voluntary_codes_by_employee: Mapping[EmployeeId, Sequence[DeductionCode]],
    ) -> PaySlip:
        earning_lines = self._earning_lines(employee, hours_by_employee.get(employee.id))
        gross = _sum_money(self._currency, (line.amount for line in earning_lines))

        ytd = self._ytd_store.get(employee.id)
        pension = self._pension_calculator.calculate(gross, ytd.pension)
        insurance = self._insurance_calculator.calculate(gross, ytd.insurance)
        tax = self._withholding_calculator.calculate(gross)

        voluntary_lines = [
            self._deduction_registry.get(code).calculate(gross)
            for code in voluntary_codes_by_employee.get(employee.id, ())
        ]
        statutory_lines = [
            DeductionLine(PENSION, pension),
            DeductionLine(INSURANCE, insurance),
            DeductionLine(TAX, tax),
        ]
        deduction_lines = sorted(
            statutory_lines + voluntary_lines, key=lambda line: str(line.code)
        )
        total_deductions = _sum_money(self._currency, (line.amount for line in deduction_lines))
        net = gross - total_deductions

        employer_pension = employer_share(pension, self._employer_pension_multiplier)
        employer_insurance = employer_share(insurance, self._employer_insurance_multiplier)
        employer_lines = (
            DeductionLine(PENSION, employer_pension),
            DeductionLine(INSURANCE, employer_insurance),
        )

        self._ytd_store.record(
            employee.id, gross=gross, pension=pension, insurance=insurance, tax=tax
        )

        return PaySlip(
            employee_id=employee.id,
            period=period,
            earnings=tuple(sorted(earning_lines, key=lambda line: str(line.code))),
            deductions=tuple(deduction_lines),
            employer_contributions=employer_lines,
            gross=gross,
            net=net,
        )

    def _earning_lines(self, employee: Employee, total_hours: Hours | None) -> list[EarningLine]:
        regular_calculator = self._earning_registry.get(REGULAR)

        if not isinstance(employee.compensation, HourlyCompensation):
            return [regular_calculator.calculate(employee, Hours.zero())]

        hours = total_hours if total_hours is not None else Hours.zero()
        threshold = self._weekly_overtime_threshold
        regular_hours = hours if hours.value <= threshold.value else threshold
        overtime_calculator = self._earning_registry.get(OVERTIME)

        return [
            regular_calculator.calculate(employee, regular_hours),
            overtime_calculator.calculate(employee, hours),
        ]
