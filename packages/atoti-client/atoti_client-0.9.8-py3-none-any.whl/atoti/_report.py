"""Reports of data loaded into tables.

Each table has a report made of several individual loading reports.

When an error occurs while loading data, a warning is displayed.
These warnings can be disabled like this::

    import logging

    logging.getLogger("atoti.loading").setLevel("ERROR")
"""

import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import final

from ._identification import TableIdentifier

_LOGGER = logging.getLogger("atoti.loading")


@final
@dataclass(frozen=True, kw_only=True)
class LoadingReport:
    """Report about the loading of a single file or operation."""

    name: str
    """Name of the loaded file or operation."""

    source: str
    """Source used to load the data."""

    loaded: int
    """Number of loaded lines."""

    errors: int
    """Number of errors."""

    duration: int
    """Duration of the loading in milliseconds."""

    error_messages: Sequence[str]
    """Messages of the errors."""


@final
@dataclass(frozen=True, kw_only=True)
class TableReport:
    """Report about the data loaded into a table.

    It is made of several :class:`LoadingReport`.
    """

    _clear_reports: Callable[[TableIdentifier], None] = field(repr=False)
    _get_reports: Callable[[TableIdentifier], list[LoadingReport]] = field(repr=False)
    _identifier: TableIdentifier

    def clear(self) -> None:
        self._clear_reports(self._identifier)

    @property
    def reports(self) -> Sequence[LoadingReport]:
        """Reports of individual loading."""
        return self._get_reports(self._identifier)

    @property
    def total_loaded(self) -> int:
        """Total number of loaded rows."""
        return sum(r.loaded for r in self.reports)

    @property
    def total_errors(self) -> int:
        """Total number of errors."""
        return sum(r.errors for r in self.reports)

    @property
    def error_messages(self) -> Sequence[str]:
        """Error messages."""
        return [message for r in self.reports for message in r.error_messages]

    @property
    def table_name(self) -> str:
        """Table name."""
        return self._identifier.table_name


def _warn_new_errors(  # pyright: ignore[reportUnusedFunction]
    errors: Mapping[str, int],
) -> None:
    """Display a warning if there are new errors."""
    for table, error_count in errors.items():
        if error_count > 0:
            message = (
                f"{error_count} error(s) occurred while feeding the table {table}."
            )
            message += " Check the session's logs for more details."
            _LOGGER.warning(message)
