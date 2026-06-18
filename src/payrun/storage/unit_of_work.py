"""An explicit transaction boundary around a connection.

Work done through repositories inside the `with` block commits together on
clean exit, or rolls back together if an exception propagates.
"""

from __future__ import annotations

import sqlite3
from types import TracebackType


class UnitOfWork:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def __enter__(self) -> sqlite3.Connection:
        return self._connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
