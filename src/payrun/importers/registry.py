"""The set of timesheet importers available by name.

This is a seam: any object implementing `Importer` can be registered under
a name. The base repository registers exactly one, the CSV dialect in
`timesheet_csv.py`.
"""

from __future__ import annotations

from payrun.errors import NotFoundError, ValidationError
from payrun.importers.base import Importer


class ImporterRegistry:
    def __init__(self) -> None:
        self._importers: dict[str, Importer] = {}

    def register(self, importer: Importer) -> None:
        if importer.name in self._importers:
            raise ValidationError(f"importer {importer.name!r} is already registered")
        self._importers[importer.name] = importer

    def get(self, name: str) -> Importer:
        try:
            return self._importers[name]
        except KeyError:
            raise NotFoundError(f"no importer registered under {name!r}") from None

    def names(self) -> list[str]:
        return sorted(self._importers)
