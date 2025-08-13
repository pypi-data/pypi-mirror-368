from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import final

from typing_extensions import override

from .._identification import MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient


@final
@dataclass(eq=False, frozen=True)
class PublishedMeasure(MeasureDefinition):
    _name: str
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
        raise RuntimeError("Cannot create a measure that already exists in the cube.")
