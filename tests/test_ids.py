import pytest

from payrun.errors import ValidationError
from payrun.ids import EmployeeId, PayRunId, PeriodId


@pytest.mark.parametrize("id_type", [EmployeeId, PayRunId, PeriodId])
def test_rejects_blank_value(id_type):
    with pytest.raises(ValidationError):
        id_type("   ")


@pytest.mark.parametrize("id_type", [EmployeeId, PayRunId, PeriodId])
def test_str_returns_underlying_value(id_type):
    assert str(id_type("E0007")) == "E0007"


def test_ids_are_frozen():
    employee_id = EmployeeId("E0007")
    with pytest.raises(AttributeError):
        employee_id.value = "E0008"  # type: ignore[misc]


def test_equal_ids_are_equal_and_hashable():
    assert EmployeeId("E0007") == EmployeeId("E0007")
    assert hash(EmployeeId("E0007")) == hash(EmployeeId("E0007"))


def test_ids_order_lexicographically():
    assert EmployeeId("E0001") < EmployeeId("E0002")


def test_different_id_types_are_not_interchangeable():
    assert EmployeeId("E0007") != PayRunId("E0007")


@pytest.mark.parametrize("id_type", [EmployeeId, PayRunId, PeriodId])
def test_rejects_empty_string(id_type):
    with pytest.raises(ValidationError):
        id_type("")


@pytest.mark.parametrize("id_type", [EmployeeId, PayRunId, PeriodId])
def test_repr_shows_the_type_and_value(id_type):
    assert repr(id_type("E0007")) == f"{id_type.__name__}(value='E0007')"
