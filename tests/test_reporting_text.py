import datetime as dt
from decimal import Decimal

from payrun.calendarx.period import PayPeriod
from payrun.ids import EmployeeId
from payrun.money import Money
from payrun.reporting.renderer import Renderer
from payrun.reporting.text import TextRenderer
from payrun.run.result import PayRunResult, PaySlip


def _period() -> PayPeriod:
    return PayPeriod(
        start=dt.date(2026, 3, 1),
        end=dt.date(2026, 3, 15),
        pay_date=dt.date(2026, 3, 20),
        sequence=1,
    )


def _payslip() -> PaySlip:
    return PaySlip(
        employee_id=EmployeeId("E0007"),
        period=_period(),
        earnings=(),
        deductions=(),
        employer_contributions=(),
        gross=Money(Decimal("2000.00"), "USD"),
        net=Money(Decimal("1800.00"), "USD"),
    )


def test_text_renderer_satisfies_the_protocol():
    assert isinstance(TextRenderer(), Renderer)


def test_render_payslip_joins_lines_with_newlines():
    rendered = TextRenderer().render_payslip(_payslip())
    assert rendered.startswith("Employee: E0007\n")
    assert "Net: 1800.00 USD" in rendered.splitlines()


def test_render_register_joins_lines_with_newlines():
    result = PayRunResult(period=_period(), payslips=(_payslip(),))
    rendered = TextRenderer().render_register(result)
    lines = rendered.splitlines()
    assert lines[0] == "Pay Run Register: 2026-03-01..2026-03-15"
    assert lines[1] == "E0007: gross=2000.00 USD net=1800.00 USD"
