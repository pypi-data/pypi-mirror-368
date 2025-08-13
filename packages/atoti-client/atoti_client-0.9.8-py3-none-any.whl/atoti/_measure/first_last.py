from dataclasses import dataclass
from typing import Literal, final

from typing_extensions import override

from .._identification import LevelIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import get_measure_name


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class FirstLast(MeasureDefinition):
    """Shift the value."""

    _underlying_measure: MeasureDefinition
    _level_identifier: LevelIdentifier
    _mode: Literal["FIRST", "LAST"]
    _partitioning: LevelIdentifier | None

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        underlying_name = get_measure_name(
            py4j_client=py4j_client,
            measure=self._underlying_measure,
            cube_name=cube_name,
        )
        return py4j_client.create_measure(
            identifier,
            "FIRST_LAST",
            underlying_name,
            self._level_identifier._java_description,
            self._mode,
            self._partitioning._java_description
            if self._partitioning is not None
            else None,
            cube_name=cube_name,
        )
