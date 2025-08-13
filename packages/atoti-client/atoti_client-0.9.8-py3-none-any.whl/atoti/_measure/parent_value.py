from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._identification import HierarchyIdentifier, MeasureIdentifier
from .._measure_convertible import MeasureConvertible
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import get_measure_name


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class ParentValue(MeasureDefinition):
    """The value of the measure for the parent."""

    _underlying_measure: MeasureDefinition | str
    _degrees: Mapping[HierarchyIdentifier, int]
    _total_value: MeasureConvertible | None
    _apply_filters: bool
    _dense: bool

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
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
        total_measure_name: str | None = (
            self._total_value._distil(
                py4j_client=py4j_client,
                cube_name=cube_name,
            ).measure_name
            if isinstance(self._total_value, MeasureDefinition)
            else None
        )
        total_literal = self._total_value if total_measure_name is None else None

        return py4j_client.create_measure(
            identifier,
            "PARENT_VALUE",
            underlying_name,
            {
                identifier._java_description: degree
                for identifier, degree in self._degrees.items()
            },
            total_measure_name,
            total_literal,
            self._apply_filters,
            self._dense,
            cube_name=cube_name,
        )
