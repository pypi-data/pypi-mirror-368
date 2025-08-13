from collections.abc import Set as AbstractSet
from dataclasses import KW_ONLY
from typing import Annotated, final

from pydantic import AfterValidator, Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._identification import Identifiable, LevelIdentifier, identify
from .._measure.calculated_measure import AggregatedMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .._validate_hierarchy_unicity import validate_hierarchy_unicity
from ._base_scope import BaseScope


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class OriginScope(BaseScope):
    """Scope performing an aggregation at the given origin.

    The input of the aggregation function will be evaluated at the given :attr:`levels` and the aggregation function will be applied "above" these intermediate aggregates.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        Using this scope with :func:`atoti.agg.mean` to average quantities summed by month:

        >>> df = pd.DataFrame(
        ...     columns=["Year", "Month", "Day", "Quantity"],
        ...     data=[
        ...         (2019, 7, 1, 15),
        ...         (2019, 7, 2, 20),
        ...         (2019, 7, 3, 30),
        ...         (2019, 6, 1, 25),
        ...         (2019, 6, 2, 15),
        ...         (2018, 7, 1, 5),
        ...         (2018, 7, 2, 10),
        ...         (2018, 6, 1, 15),
        ...         (2018, 6, 2, 5),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     default_values={"Year": 0, "Month": 0, "Day": 0},
        ...     table_name="Origin",
        ... )
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Date"] = [table["Year"], table["Month"], table["Day"]]
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> m["Average of monthly quantities"] = tt.agg.mean(
        ...     m["Quantity.SUM"], scope=tt.OriginScope({l["Month"]})
        ... )

        :guilabel:`Average of monthly quantities` will evaluate :guilabel:`Quantity.SUM` for each :guilabel:`Month` and average these values "above" this level:

        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Average of monthly quantities"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Average of monthly quantities
        Year  Month Day
        Total                    140                         35.00
        2018                      35                         17.50
              6                   20                         20.00
                    1             15                         15.00
                    2              5                          5.00
              7                   15                         15.00
                    1              5                          5.00
                    2             10                         10.00
        2019                     105                         52.50
              6                   40                         40.00
                    1             25                         25.00
                    2             15                         15.00
              7                   65                         65.00
                    1             15                         15.00
                    2             20                         20.00
                    3             30                         30.00

        The aggregation function can be changed again to compute the max of these averages:

        >>> m["Max average of monthly quantities"] = tt.agg.max(
        ...     m["Average of monthly quantities"],
        ...     scope=tt.OriginScope({l["Year"]}),
        ... )
        >>> cube.query(
        ...     m["Average of monthly quantities"],
        ...     m["Max average of monthly quantities"],
        ...     levels=[l["Year"]],
        ...     include_totals=True,
        ... )
              Average of monthly quantities Max average of monthly quantities
        Year
        Total                         35.00                             52.50
        2018                          17.50                             17.50
        2019                          52.50                             52.50

    """

    levels: Annotated[
        AbstractSet[Identifiable[LevelIdentifier]],
        Field(min_length=1),
        AfterValidator(validate_hierarchy_unicity),
    ]
    """The levels constituting the origin of the aggregation."""

    _: KW_ONLY

    @override
    def _create_measure_definition(
        self,
        measure: VariableMeasureConvertible,
        /,
        *,
        plugin_key: str,
    ) -> MeasureDefinition:
        return AggregatedMeasure(
            _underlying_measure=measure,
            _plugin_key=plugin_key,
            _on_levels=frozenset(identify(level) for level in self.levels),
        )
