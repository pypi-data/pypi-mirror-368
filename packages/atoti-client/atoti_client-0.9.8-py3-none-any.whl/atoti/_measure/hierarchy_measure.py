from dataclasses import KW_ONLY, dataclass
from typing import final

from typing_extensions import override

from .._identification import HierarchyIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient


@final
@dataclass(eq=False, frozen=True)
class HierarchyMeasure(MeasureDefinition):
    _hierarchy_identifier: HierarchyIdentifier
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
            "HIERARCHY",
            self._hierarchy_identifier._java_description,
            cube_name=cube_name,
        )
