from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._identification import HierarchyIdentifier, Identifiable, identify
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._base_scope import BaseScope


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class SiblingsScope(BaseScope):
    """Scope performing a "siblings" aggregation.

    The aggregated value for each member of a given level in :attr:`hierarchy` is computed by aggregating all the members with the same parents (i.e. its siblings) with the given function.

    A siblings aggregation is appropriate for operations such as marginal aggregations (e.g. marginal VaR, marginal mean) for non-linear aggregation functions.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        Using this scope with :func:`atoti.agg.sum` to perform a "siblings" sum:

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["Date", "Quantity"],
        ...     data=[
        ...         (date(2019, 7, 1), 15),
        ...         (date(2019, 7, 2), 20),
        ...         (date(2019, 7, 3), 30),
        ...         (date(2019, 6, 1), 25),
        ...         (date(2019, 6, 2), 15),
        ...         (date(2018, 7, 1), 5),
        ...         (date(2018, 7, 2), 10),
        ...         (date(2018, 6, 1), 15),
        ...         (date(2018, 6, 2), 5),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, table_name="Siblings")
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> cube.create_date_hierarchy("Date", column=table["Date"])
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> m["Siblings quantity"] = tt.agg.sum(
        ...     m["Quantity.SUM"], scope=tt.SiblingsScope(h["Date"])
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Siblings quantity"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Siblings quantity
        Year  Month Day
        Total                    140               140
        2018                      35               140
              6                   20                35
                    1             15                20
                    2              5                20
              7                   15                35
                    1              5                15
                    2             10                15
        2019                     105               140
              6                   40               105
                    1             25                40
                    2             15                40
              7                   65               105
                    1             15                65
                    2             20                65
                    3             30                65

        Using :attr:`exclude_self`:

        >>> m["Siblings quantity excluding self"] = tt.agg.sum(
        ...     m["Quantity.SUM"],
        ...     scope=tt.SiblingsScope(h["Date"], exclude_self=True),
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Siblings quantity excluding self"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Siblings quantity excluding self
        Year  Month Day
        Total                    140                                0
        2018                      35                              105
              6                   20                               15
                    1             15                                5
                    2              5                               15
              7                   15                               20
                    1              5                               10
                    2             10                                5
        2019                     105                               35
              6                   40                               65
                    1             25                               15
                    2             15                               25
              7                   65                               40
                    1             15                               50
                    2             20                               45
                    3             30                               35

    """

    hierarchy: Identifiable[HierarchyIdentifier]
    """The hierarchy along which the aggregation will be performed."""

    _: KW_ONLY

    exclude_self: bool = False
    """If ``True``, the current member will not contribute to its aggregated value."""

    @override
    def _create_measure_definition(
        self,
        measure: VariableMeasureConvertible,
        /,
        *,
        plugin_key: str,
    ) -> MeasureDefinition:
        return GenericMeasure(
            "SIBLINGS_AGG",
            measure,
            identify(self.hierarchy)._java_description,
            plugin_key,
            self.exclude_self,
        )
