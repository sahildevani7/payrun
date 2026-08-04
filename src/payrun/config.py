"""Flat configuration loading.

Configuration is a small, flat JSON document. There is no nesting, no
environment-variable interpolation, and no implicit defaulting of required
keys — a missing key is a `ConfigurationError`, not a silent fallback.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from payrun.calendarx.frequency import Frequency
from payrun.errors import ConfigurationError
from payrun.money import CURRENCY_EXPONENTS

_REQUIRED_KEYS = ("database_path", "currency", "plan_year", "frequency")


@dataclass(frozen=True, slots=True)
class Config:
    database_path: str
    currency: str
    plan_year: int
    frequency: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Config:
        missing = [key for key in _REQUIRED_KEYS if key not in data]
        if missing:
            raise ConfigurationError(f"missing config keys: {', '.join(sorted(missing))}")
        try:
            config = cls(
                database_path=str(data["database_path"]),
                currency=str(data["currency"]),
                plan_year=int(data["plan_year"]),
                frequency=str(data["frequency"]),
            )
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"malformed config value: {exc}") from exc

        if config.currency not in CURRENCY_EXPONENTS:
            raise ConfigurationError(f"unknown currency {config.currency!r}")
        if config.frequency not in {frequency.value for frequency in Frequency}:
            raise ConfigurationError(f"unknown frequency {config.frequency!r}")
        return config


def load_config(path: Path) -> Config:
    try:
        raw = path.read_text()
    except OSError as exc:
        raise ConfigurationError(f"cannot read config file {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"config file {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"config file {path} must contain a JSON object")
    return Config.from_mapping(data)
