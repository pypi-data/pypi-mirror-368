from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._identification import (
    ColumnIdentifier,
    HierarchyIdentifier,
    MeasureIdentifier,
)
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .._py4j_client._utils import to_java_list
from .utils import get_measure_name


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class ConsolidateMeasure(MeasureDefinition):
    _underlying_measure: MeasureDefinition | str
    _hierarchy: HierarchyIdentifier
    _level_columns: tuple[ColumnIdentifier, ...]
    _factors: tuple[ColumnIdentifier, ...]

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        underlying_name = (
            self._underlying_measure
            if isinstance(self._underlying_measure, str)
            else get_measure_name(
                py4j_client=py4j_client,
                measure=self._underlying_measure,
                cube_name=cube_name,
            )
        )

        return py4j_client.create_measure(
            identifier,
            "ALTERNATE_HIERARCHY_MEASURE",
            underlying_name,
            self._hierarchy._java_description,
            self._factors[0].table_identifier.table_name,
            to_java_list(
                [column.column_name for column in self._level_columns],
                gateway=py4j_client.gateway,
            ),
            to_java_list(
                [column.column_name for column in self._factors],
                gateway=py4j_client.gateway,
            ),
            cube_name=cube_name,
        )
