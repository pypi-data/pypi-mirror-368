from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._identification import LevelIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import get_measure_name


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class DateShift(MeasureDefinition):
    """Shift the value."""

    _underlying_measure: MeasureDefinition
    _level_identifier: LevelIdentifier
    _shift: str
    _method: str

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        underlying_name = get_measure_name(
            py4j_client=py4j_client,
            measure=self._underlying_measure,
            cube_name=cube_name,
        )
        return py4j_client.create_measure(
            identifier,
            "DATE_SHIFT",
            underlying_name,
            self._level_identifier._java_description,
            self._shift,
            self._method,
            cube_name=cube_name,
        )
