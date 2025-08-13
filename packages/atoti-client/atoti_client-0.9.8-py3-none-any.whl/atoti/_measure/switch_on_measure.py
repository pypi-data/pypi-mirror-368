from collections.abc import Mapping
from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._constant import Constant
from .._identification import LevelIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .._py4j_client._utils import to_java_map, to_java_object


@final
@dataclass(repr=True, frozen=True, kw_only=True)
class SwitchOnMeasure(MeasureDefinition):
    """A measure that switches between different measures based on the value of a level."""

    _subject: LevelIdentifier
    _cases: Mapping[Constant, MeasureDefinition]
    _default: MeasureDefinition | None = None
    _above_level: MeasureDefinition | None = None

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        return py4j_client.create_measure(
            identifier,
            "SWITCH_ON",
            py4j_client.gateway.jvm.com.activeviam.activepivot.core.intf.api.cube.metadata.LevelIdentifier.fromDescription(  # pyright: ignore[reportCallIssue,reportAttributeAccessIssue,reportOptionalCall,reportOptionalMemberAccess] # spell-checker: disable-line
                self._subject._java_description,  # pyright: ignore[reportCallIssue]
            ),
            to_java_map(
                {
                    to_java_object(key, gateway=py4j_client.gateway): value._distil(
                        py4j_client=py4j_client,
                        cube_name=cube_name,
                    ).measure_name
                    for key, value in self._cases.items()
                },
                gateway=py4j_client.gateway,
            ),
            None
            if self._default is None
            else self._default._distil(
                py4j_client=py4j_client,
                cube_name=cube_name,
            ).measure_name,
            None
            if self._above_level is None
            else self._above_level._distil(
                py4j_client=py4j_client,
                cube_name=cube_name,
            ).measure_name,
            cube_name=cube_name,
        )
