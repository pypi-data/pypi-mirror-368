from __future__ import annotations

from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._constant import Constant
from .._identification import MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .._py4j_client._utils import to_java_object
from .._pydantic import PYDANTIC_CONFIG


@final
@dataclass(config=PYDANTIC_CONFIG, eq=False, frozen=True, kw_only=True)
class ConstantMeasure(MeasureDefinition):
    """A measure equal to a constant."""

    _value: Constant

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        value = to_java_object(self._value, gateway=py4j_client.gateway)
        return py4j_client.create_measure(
            identifier,
            "CONSTANT",
            value,
            cube_name=cube_name,
        )
