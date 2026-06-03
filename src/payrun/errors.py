"""Typed error hierarchy for payrun.

Every failure in the codebase raises one of these. No bare ``ValueError`` and
no ``assert`` used for validation outside this module.
"""

from __future__ import annotations


class PayrunError(Exception):
    """Base class for every error payrun raises."""


class ValidationError(PayrunError):
    """A value failed validation at a domain boundary."""


class CurrencyMismatchError(PayrunError):
    """Two `Money` values with different currencies were combined."""

    def __init__(self, left: str, right: str) -> None:
        self.left = left
        self.right = right
        super().__init__(f"cannot combine currency {left!r} with currency {right!r}")


class ConfigurationError(PayrunError):
    """The runtime configuration is missing or malformed."""


class ParameterNotFoundError(PayrunError):
    """A statutory parameter lookup found no data for the requested key."""

    def __init__(self, plan_year: int, key: str) -> None:
        self.plan_year = plan_year
        self.key = key
        super().__init__(f"no parameter {key!r} for plan year {plan_year}")


class StorageError(PayrunError):
    """A storage-layer operation failed."""


class MigrationError(StorageError):
    """The migration runner could not apply or verify a migration."""


class ImporterError(PayrunError):
    """A timesheet import could not be parsed or validated."""


class RunError(PayrunError):
    """A pay run could not be validated or executed."""


class NotFoundError(PayrunError):
    """A lookup by identifier found no matching record."""
