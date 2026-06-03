import pytest

from payrun.errors import (
    ConfigurationError,
    CurrencyMismatchError,
    ImporterError,
    MigrationError,
    NotFoundError,
    ParameterNotFoundError,
    PayrunError,
    RunError,
    StorageError,
    ValidationError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        ValidationError,
        ConfigurationError,
        StorageError,
        ImporterError,
        RunError,
        NotFoundError,
    ],
)
def test_direct_subclasses_are_payrun_errors(error_type):
    assert issubclass(error_type, PayrunError)


def test_migration_error_is_a_storage_error():
    assert issubclass(MigrationError, StorageError)
    assert issubclass(MigrationError, PayrunError)


def test_currency_mismatch_error_message_names_both_currencies():
    error = CurrencyMismatchError("USD", "CAD")
    assert "USD" in str(error)
    assert "CAD" in str(error)
    assert error.left == "USD"
    assert error.right == "CAD"


def test_parameter_not_found_error_message_names_year_and_key():
    error = ParameterNotFoundError(2026, "pension_rate")
    assert "2026" in str(error)
    assert "pension_rate" in str(error)
