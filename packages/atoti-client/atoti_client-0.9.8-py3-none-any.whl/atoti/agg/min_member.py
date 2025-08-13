from __future__ import annotations

from .._doc import doc
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..level import Level
from ._utils import EXTREMUM_MEMBER_DOC as _EXTREMUM_MEMBER_DOC


@doc(
    _EXTREMUM_MEMBER_DOC,
    op="min",
    example="""
        >>> m["City with minimum price"] = tt.agg.min_member(m["Price"], l["City"])

        At the given level, the measure is equal to the current member of the City level:

        >>> cube.query(m["City with minimum price"], levels=[l["City"]])
                               City with minimum price
        Continent     City
        Europe        Berlin                    Berlin
                      London                    London
                      Paris                      Paris
        North America New York                New York

        At a level above it, the measure is equal to the city of each continent with the minimum price:

        >>> cube.query(m["City with minimum price"], levels=[l["Continent"]])
                      City with minimum price
        Continent
        Europe                         Berlin
        North America                New York

        At the top level, the measure is equal to the city with the minimum price across all continents:

        >>> cube.query(m["City with minimum price"])
          City with minimum price
        0                  Berlin""".replace("\n", "", 1),
)
def min_member(
    measure: VariableMeasureConvertible,
    /,
    level: Level,
) -> MeasureDefinition:
    is_max = False
    return GenericMeasure(
        "COMPARABLE_MAX",
        measure,
        level._identifier._java_description,
        is_max,
        "MEMBER",
    )
