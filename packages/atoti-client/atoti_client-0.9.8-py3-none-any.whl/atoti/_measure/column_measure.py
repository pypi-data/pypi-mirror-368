from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._identification import ColumnIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class ColumnMeasure(MeasureDefinition):
    """Measure based on the column of a table."""

    _column_identifier: ColumnIdentifier
    _plugin_key: str

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        return py4j_client.aggregated_measure(
            identifier,
            self._plugin_key,
            column_identifier=self._column_identifier,
            cube_name=cube_name,
        )
