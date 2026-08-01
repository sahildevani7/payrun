import datetime as dt
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.flat import FlatDeductionCalculator
from payrun.deductions.registry import DeductionRegistry
from payrun.earnings.overtime import default_calculator
from payrun.earnings.registry import EarningRegistry
from payrun.earnings.regular import RegularEarningCalculator
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.run.engine import PayRunEngine
from payrun.run.ytd import YtdStore
from payrun.statutory.insurance import InsuranceCalculator
from payrun.statutory.pension import PensionCalculator
from payrun.statutory.tables import load_parameters
from payrun.tax.withholding import WithholdingCalculator


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 31),
        pay_date=dt.date(2026, 4, 5),
        sequence=3,
    )


def _build_engine(frequency: Frequency, with_parking_deduction: bool = False) -> PayRunEngine:
    earning_registry = EarningRegistry()
    earning_registry.register(RegularEarningCalculator())
    earning_registry.register(default_calculator())

    deduction_registry = DeductionRegistry()
    if with_parking_deduction:
        deduction_registry.register(
            FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
        )

    params = load_parameters(2026)
    return PayRunEngine(
        currency="USD",
        earning_registry=earning_registry,
        deduction_registry=deduction_registry,
        weekly_overtime_threshold=Hours(Decimal("40")),
        pension_calculator=PensionCalculator(params.pension, frequency),
        insurance_calculator=InsuranceCalculator(params.insurance),
        withholding_calculator=WithholdingCalculator(params.tax, frequency),
        employer_pension_multiplier=params.employer.pension_multiplier,
        employer_insurance_multiplier=params.employer.insurance_multiplier,
        ytd_store=YtdStore("USD"),
    )


def _salaried(employee_id: str) -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.MONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )


def _hourly(employee_id: str, rate: str = "30.00") -> Employee:
    return Employee(
        id=EmployeeId(employee_id),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.MONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal(rate), "USD")),
    )


def test_net_equals_gross_minus_all_deductions():
    engine = _build_engine(Frequency.MONTHLY)
    result = engine.run([_salaried("E0001")], _period(), {})
    payslip = result.payslip_for(EmployeeId("E0001"))
    total_deductions = sum((line.amount for line in payslip.deductions), Money.zero("USD"))
    assert payslip.net == payslip.gross - total_deductions


def test_gross_equals_sum_of_earning_lines():
    engine = _build_engine(Frequency.MONTHLY)
    result = engine.run([_salaried("E0001")], _period(), {})
    payslip = result.payslip_for(EmployeeId("E0001"))
    total_earnings = sum((line.amount for line in payslip.earnings), Money.zero("USD"))
    assert payslip.gross == total_earnings


def test_hourly_overtime_does_not_double_count_straight_time():
    engine = _build_engine(Frequency.MONTHLY)
    hours = {EmployeeId("E0002"): Hours(Decimal("45"))}
    result = engine.run([_hourly("E0002", "20.00")], _period(), hours)
    payslip = result.payslip_for(EmployeeId("E0002"))
    regular = next(line for line in payslip.earnings if str(line.code) == "REGULAR")
    overtime = next(line for line in payslip.earnings if str(line.code) == "OVERTIME")
    # 40 regular hours at 20.00 + 5 overtime hours at 20.00*1.5
    assert regular.amount == Money(Decimal("800.00"), "USD")
    assert overtime.amount == Money(Decimal("150.00"), "USD")
    assert payslip.gross == Money(Decimal("950.00"), "USD")


def test_hourly_below_threshold_has_no_overtime():
    engine = _build_engine(Frequency.MONTHLY)
    hours = {EmployeeId("E0002"): Hours(Decimal("30"))}
    result = engine.run([_hourly("E0002", "20.00")], _period(), hours)
    payslip = result.payslip_for(EmployeeId("E0002"))
    overtime = next(line for line in payslip.earnings if str(line.code) == "OVERTIME")
    assert overtime.amount == Money.zero("USD")


def test_payslips_are_sorted_by_employee_id():
    engine = _build_engine(Frequency.MONTHLY)
    result = engine.run([_salaried("E0009"), _salaried("E0001")], _period(), {})
    assert [str(p.employee_id) for p in result.payslips] == ["E0001", "E0009"]


def test_ytd_accumulates_gross_across_two_runs():
    engine = _build_engine(Frequency.MONTHLY)
    employee = _salaried("E0001")
    first = engine.run([employee], _period(), {})
    second_period = PayPeriod(
        start=dt.date(2026, 4, 1),
        end=dt.date(2026, 4, 30),
        pay_date=dt.date(2026, 5, 5),
        sequence=4,
    )
    second = engine.run([employee], second_period, {})
    first_gross = first.payslip_for(EmployeeId("E0001")).gross
    second_gross = second.payslip_for(EmployeeId("E0001")).gross
    assert first_gross == second_gross
    ytd = engine.ytd_store.get(EmployeeId("E0001"))
    assert ytd.gross == first_gross + second_gross


def test_voluntary_deduction_reduces_net():
    engine_without = _build_engine(Frequency.MONTHLY, with_parking_deduction=False)
    without = engine_without.run([_salaried("E0001")], _period(), {})

    engine_with = _build_engine(Frequency.MONTHLY, with_parking_deduction=True)
    with_result = engine_with.run(
        [_salaried("E0001")],
        _period(),
        {},
        voluntary_codes_by_employee={EmployeeId("E0001"): [DeductionCode("PARKING")]},
    )

    net_without = without.payslip_for(EmployeeId("E0001")).net
    net_with = with_result.payslip_for(EmployeeId("E0001")).net
    assert net_with == net_without - Money(Decimal("25.00"), "USD")


def test_employer_contributions_use_the_configured_multiplier():
    engine = _build_engine(Frequency.MONTHLY)
    result = engine.run([_hourly("E0002")], _period(), {EmployeeId("E0002"): Hours(Decimal("40"))})
    payslip = result.payslip_for(EmployeeId("E0002"))
    employee_pension = next(
        line.amount for line in payslip.deductions if str(line.code) == "PENSION"
    )
    employer_pension = next(
        line.amount for line in payslip.employer_contributions if str(line.code) == "PENSION"
    )
    # employer pension multiplier for plan year 2026 is a dollar-for-dollar match
    assert employer_pension == employee_pension


def test_mixed_hourly_and_salaried_employees_in_one_run():
    engine = _build_engine(Frequency.MONTHLY)
    hours = {EmployeeId("E0002"): Hours(Decimal("40"))}
    result = engine.run([_salaried("E0001"), _hourly("E0002")], _period(), hours)
    assert {str(p.employee_id) for p in result.payslips} == {"E0001", "E0002"}


def test_deductions_are_sorted_by_code():
    engine = _build_engine(Frequency.MONTHLY, with_parking_deduction=True)
    result = engine.run(
        [_salaried("E0001")],
        _period(),
        {},
        voluntary_codes_by_employee={EmployeeId("E0001"): [DeductionCode("PARKING")]},
    )
    payslip = result.payslip_for(EmployeeId("E0001"))
    codes = [str(line.code) for line in payslip.deductions]
    assert codes == sorted(codes)


def test_earnings_are_sorted_by_code():
    engine = _build_engine(Frequency.MONTHLY)
    result = engine.run(
        [_hourly("E0002")], _period(), {EmployeeId("E0002"): Hours(Decimal("45"))}
    )
    payslip = result.payslip_for(EmployeeId("E0002"))
    codes = [str(line.code) for line in payslip.earnings]
    assert codes == ["OVERTIME", "REGULAR"]
