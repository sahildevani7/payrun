import pytest

from payrun.errors import NotFoundError, ValidationError
from payrun.importers.base import Importer
from payrun.importers.registry import ImporterRegistry
from payrun.importers.timesheet_csv import TimesheetCsvImporter


def test_register_then_get_returns_the_same_importer():
    registry = ImporterRegistry()
    importer = TimesheetCsvImporter()
    registry.register(importer)
    assert registry.get("timesheet_csv") is importer


def test_get_missing_name_raises_not_found():
    registry = ImporterRegistry()
    with pytest.raises(NotFoundError):
        registry.get("timesheet_csv")


def test_register_duplicate_name_raises_validation_error():
    registry = ImporterRegistry()
    registry.register(TimesheetCsvImporter())
    with pytest.raises(ValidationError):
        registry.register(TimesheetCsvImporter())


def test_names_are_sorted():
    registry = ImporterRegistry()
    registry.register(TimesheetCsvImporter())
    assert registry.names() == ["timesheet_csv"]


def test_timesheet_csv_importer_satisfies_the_protocol():
    assert isinstance(TimesheetCsvImporter(), Importer)
