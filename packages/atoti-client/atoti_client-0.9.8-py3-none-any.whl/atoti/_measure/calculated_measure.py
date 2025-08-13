from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import KW_ONLY, dataclass
from typing import final

from typing_extensions import override

from .._identification import LevelIdentifier, MeasureIdentifier
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import convert_measure_args

_Operand = MeasureDefinition | str


@final
@dataclass(frozen=True)
class Operator:
    """An operator to create a calculated measure from other measures."""

    _name: str
    _operands: Sequence[_Operand]
    _: KW_ONLY


@final
@dataclass(eq=False, frozen=True)
class CalculatedMeasure(MeasureDefinition):
    """A calculated measure is the result of an operation between other measures."""

    _operator: Operator
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
            "CALCULATED",
            self._operator._name,
            convert_measure_args(
                py4j_client=py4j_client,
                cube_name=cube_name,
                args=self._operator._operands,
            ),
            cube_name=cube_name,
        )


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class AggregatedMeasure(MeasureDefinition):
    """Aggregated measure."""

    _underlying_measure: VariableMeasureConvertible
    _plugin_key: str
    _on_levels: Collection[LevelIdentifier] = ()

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
            "LEAF_AGGREGATION",
            *convert_measure_args(
                py4j_client=py4j_client,
                cube_name=cube_name,
                args=(self._underlying_measure,),
            ),
            [
                level_identifier._java_description
                for level_identifier in self._on_levels
            ],
            self._plugin_key,
            cube_name=cube_name,
        )
