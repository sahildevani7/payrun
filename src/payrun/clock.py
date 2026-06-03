"""Clock protocol. Every date-consuming call takes a `Clock`.

`SystemClock` is the only class in this codebase permitted to call the
standard library's real-time clock. Everything else, including tests, uses
`FixedClock` so runs are reproducible.
"""

from __future__ import annotations

import datetime as _datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Something that can report the current date and datetime."""

    def today(self) -> _datetime.date: ...

    def now(self) -> _datetime.datetime: ...


class FixedClock:
    """A clock pinned to a single instant, for deterministic runs and tests."""

    def __init__(self, instant: _datetime.datetime) -> None:
        if instant.tzinfo is not None:
            raise ValueError("FixedClock requires a naive datetime")
        self._instant = instant

    def today(self) -> _datetime.date:
        return self._instant.date()

    def now(self) -> _datetime.datetime:
        return self._instant

    @classmethod
    def at(cls, year: int, month: int, day: int) -> FixedClock:
        return cls(_datetime.datetime(year, month, day))


class SystemClock:
    """The only clock allowed to read the real wall-clock time."""

    def today(self) -> _datetime.date:
        return _datetime.date.today()

    def now(self) -> _datetime.datetime:
        return _datetime.datetime.now()
