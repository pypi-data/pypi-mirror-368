from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import final

from typing_extensions import override

from .._identification import MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import convert_measure_args


@final
@dataclass(eq=False, frozen=True)
class BooleanMeasure(MeasureDefinition):
    """Boolean operation between measures."""

    _operator: str
    _operands: tuple[MeasureDefinition, ...]
    _: KW_ONLY

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        return py4j_client.create_measure(
            identifier,
            "BOOLEAN",
            self._operator,
            convert_measure_args(
                py4j_client=py4j_client,
                cube_name=cube_name,
                args=self._operands,
            ),
            cube_name=cube_name,
        )
