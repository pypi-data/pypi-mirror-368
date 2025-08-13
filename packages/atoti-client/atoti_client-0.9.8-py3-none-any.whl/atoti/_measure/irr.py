from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._identification import HierarchyIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class IrrMeasure(MeasureDefinition):
    _cash_flows_measure: MeasureDefinition
    _market_value_measure: MeasureDefinition
    _date_hierarchy_identifier: HierarchyIdentifier
    _precision: float
    _period: str
    _guess: float | None

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        # Distil the underlying measures
        cash_flows_name: str = self._cash_flows_measure._distil(
            py4j_client=py4j_client,
            cube_name=cube_name,
        ).measure_name
        market_value_name: str = self._market_value_measure._distil(
            py4j_client=py4j_client,
            cube_name=cube_name,
        ).measure_name

        return py4j_client.create_measure(
            identifier,
            "IRR",
            market_value_name,  # market value first
            cash_flows_name,
            self._date_hierarchy_identifier._java_description,
            self._precision,
            self._period,
            self._guess,
            cube_name=cube_name,
        )
