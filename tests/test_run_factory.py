import datetime as dt
from decimal import Decimal

from payrun.calendarx.frequency import Frequency
from payrun.calendarx.period import PayPeriod
from payrun.deductions.code import DeductionCode
from payrun.deductions.flat import FlatDeductionCalculator
from payrun.hours import Hours
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.people.compensation import HourlyCompensation, SalariedCompensation
from payrun.people.employee import Employee
from payrun.people.employment import Employment, EmploymentStatus
from payrun.run.factory import build_engine
from payrun.run.ytd import YtdStore


def _employee() -> Employee:
    return Employee(
        id=EmployeeId("E0001"),
        first_name="Jordan",
        last_name="Lee",
        frequency=Frequency.MONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=SalariedCompensation(Money(Decimal("78000.00"), "USD")),
    )


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 31),
        pay_date=dt.date(2026, 4, 5),
        sequence=3,
    )


def test_build_engine_produces_a_working_engine():
    engine = build_engine(
        currency="USD",
        plan_year=2026,
        frequency=Frequency.MONTHLY,
        ytd_store=YtdStore("USD"),
    )
    result = engine.run([_employee()], _period(), {})
    assert result.payslip_for(EmployeeId("E0001")).gross == Money(Decimal("6500.00"), "USD")


def test_build_engine_registers_regular_and_overtime():
    engine = build_engine(
        currency="USD",
        plan_year=2026,
        frequency=Frequency.MONTHLY,
        ytd_store=YtdStore("USD"),
    )
    result = engine.run([_employee()], _period(), {})
    codes = {str(line.code) for line in result.payslip_for(EmployeeId("E0001")).earnings}
    assert codes == {"REGULAR"}


def test_build_engine_accepts_extra_deduction_calculators():
    parking = FlatDeductionCalculator(DeductionCode("PARKING"), Money(Decimal("25.00"), "USD"))
    engine = build_engine(
        currency="USD",
        plan_year=2026,
        frequency=Frequency.MONTHLY,
        ytd_store=YtdStore("USD"),
        extra_deduction_calculators=[parking],
    )
    result = engine.run(
        [_employee()],
        _period(),
        {},
        voluntary_codes_by_employee={EmployeeId("E0001"): [DeductionCode("PARKING")]},
    )
    payslip = result.payslip_for(EmployeeId("E0001"))
    assert any(str(line.code) == "PARKING" for line in payslip.deductions)


def test_build_engine_uses_the_given_ytd_store():
    ytd_store = YtdStore("USD")
    engine = build_engine(
        currency="USD",
        plan_year=2026,
        frequency=Frequency.MONTHLY,
        ytd_store=ytd_store,
    )
    engine.run([_employee()], _period(), {})
    assert ytd_store.get(EmployeeId("E0001")).gross == Money(Decimal("6500.00"), "USD")


def test_custom_overtime_threshold_is_applied():
    hourly_employee = Employee(
        id=EmployeeId("E0002"),
        first_name="Ada",
        last_name="Okafor",
        frequency=Frequency.MONTHLY,
        employment=Employment(hire_date=dt.date(2020, 1, 1), status=EmploymentStatus.ACTIVE),
        compensation=HourlyCompensation(Money(Decimal("20.00"), "USD")),
    )
    engine = build_engine(
        currency="USD",
        plan_year=2026,
        frequency=Frequency.MONTHLY,
        ytd_store=YtdStore("USD"),
        weekly_overtime_threshold=Hours(Decimal("35")),
    )
    result = engine.run([hourly_employee], _period(), {EmployeeId("E0002"): Hours(Decimal("38"))})
    overtime = next(
        line
        for line in result.payslip_for(EmployeeId("E0002")).earnings
        if str(line.code) == "OVERTIME"
    )
    assert overtime.hours == Hours(Decimal("3"))
