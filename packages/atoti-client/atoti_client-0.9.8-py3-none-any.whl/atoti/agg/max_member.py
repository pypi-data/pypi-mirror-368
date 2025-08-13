from __future__ import annotations

from .._doc import doc
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..level import Level
from ._utils import EXTREMUM_MEMBER_DOC as _EXTREMUM_MEMBER_DOC


@doc(
    _EXTREMUM_MEMBER_DOC,
    op="max",
    example="""
        >>> m["City with maximum price"] = tt.agg.max_member(m["Price"], l["City"])

        At the given level, the measure is equal to the current member of the City level:

        >>> cube.query(m["City with maximum price"], levels=[l["City"]])
                               City with maximum price
        Continent     City
        Europe        Berlin                    Berlin
                      London                    London
                      Paris                      Paris
        North America New York                New York

        At a level above it, the measure is equal to the city of each continent with the maximum price:

        >>> cube.query(m["City with maximum price"], levels=[l["Continent"]])
                      City with maximum price
        Continent
        Europe                         London
        North America                New York

        At the top level, the measure is equal to the city with the maximum price across all continents:

        >>> cube.query(m["City with maximum price"])
          City with maximum price
        0                New York""".replace("\n", "", 1),
)
def max_member(
    measure: VariableMeasureConvertible,
    /,
    level: Level,
) -> MeasureDefinition:
    is_max = True
    return GenericMeasure(
        "COMPARABLE_MAX",
        measure,
        level._identifier._java_description,
        is_max,
        "MEMBER",
    )
