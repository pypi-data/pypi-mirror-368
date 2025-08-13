from __future__ import annotations

from typing import Literal, TypeAlias, final

from typing_extensions import NotRequired, TypedDict, Unpack

from .._check_column_condition_table import check_column_condition_table
from .._constant import Constant
from .._identification import ColumnIdentifier
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import (
    MeasureConvertible,
    MeasureConvertibleIdentifier,
    MeasureOperation,
)
from .._measure_definition import (
    MeasureDefinition,
    convert_operand_to_measure_definition,
)
from .._operation import LogicalCondition, RelationalCondition, dict_from_condition
from ..column import Column

_MappingLeafCondition: TypeAlias = RelationalCondition[
    ColumnIdentifier,
    Literal["=="],
    Constant | MeasureConvertibleIdentifier | MeasureOperation,
]
_MappingCondition: TypeAlias = (
    _MappingLeafCondition | LogicalCondition[_MappingLeafCondition, Literal["&"]]
)


@final
class _LookupPrivateParameters(TypedDict):
    helper: NotRequired[MeasureConvertible]


def lookup(
    column: Column,
    mapping: _MappingCondition,
    /,
    **kwargs: Unpack[_LookupPrivateParameters],
) -> MeasureDefinition:
    """Return a measure equal to a get-by-key query on the given table column.

    Args:
        column: The column to get the value from.
        mapping: A condition made of equality checks on all the :attr:`~atoti.Table.keys` of the passed *column*'s :class:`~atoti.Table`.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> budget_dataframe = pd.DataFrame(
        ...     {
        ...         "Position": [
        ...             "Sales manager 1",
        ...             "Sales person 1",
        ...             "Sales person 2",
        ...             "Sales manager 2",
        ...             "Sales person 3",
        ...         ],
        ...         "Budget": [20000, 15000, 10000, 40000, 12000],
        ...     }
        ... )
        >>> organization_dataframe = pd.DataFrame(
        ...     {
        ...         "Supervisors 1": [
        ...             "Sales manager 1",
        ...             "Sales manager 2",
        ...         ],
        ...         "Supervisors 2": ["Sales person 1", "Sales person 3"],
        ...         "Supervisors 3": ["Sales person 2", ""],
        ...     }
        ... )
        >>> budget_table = session.read_pandas(
        ...     budget_dataframe, keys={"Position"}, table_name="Budget"
        ... )
        >>> organization_table = session.read_pandas(
        ...     organization_dataframe,
        ...     keys={"Supervisors 1"},
        ...     table_name="Company organization",
        ... )
        >>> cube = session.create_cube(organization_table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Organization level"] = [
        ...     organization_table["Supervisors 1"],
        ...     organization_table["Supervisors 2"],
        ...     organization_table["Supervisors 3"],
        ... ]
        >>> m["Position"] = tt.where(
        ...     (~l["Supervisors 1"].isnull()) & (l["Supervisors 2"].isnull()),
        ...     l["Supervisors 1"],
        ...     tt.where(
        ...         (~l["Supervisors 2"].isnull()) & (l["Supervisors 3"].isnull()),
        ...         l["Supervisors 2"],
        ...         l["Supervisors 3"],
        ...     ),
        ... )
        >>> cube.query(m["Position"], levels=[l["Supervisors 3"]], include_totals=True)
                                                              Position
        Supervisors 1   Supervisors 2  Supervisors 3
        Sales manager 1                                Sales manager 1
                        Sales person 1                  Sales person 1
                                       Sales person 2   Sales person 2
        Sales manager 2                                Sales manager 2
                        Sales person 3                  Sales person 3
                                       N/A                         N/A
        >>> m["Position budget"] = tt.lookup(
        ...     budget_table["Budget"], budget_table["Position"] == m["Position"]
        ... )
        >>> cube.query(
        ...     m["Position budget"], levels=[l["Supervisors 3"]], include_totals=True
        ... )
                                                      Position budget
        Supervisors 1   Supervisors 2  Supervisors 3
        Sales manager 1                                        20,000
                        Sales person 1                         15,000
                                       Sales person 2          10,000
        Sales manager 2                                        40,000
                        Sales person 3                         12,000
    """
    check_column_condition_table(
        mapping,
        attribute_name="subject",
        expected_table_identifier=column._identifier.table_identifier,
    )
    return GenericMeasure(
        "LOOKUP",
        column._identifier.table_identifier.table_name,
        {
            subject.column_name: convert_operand_to_measure_definition(target)
            for subject, target in dict_from_condition(mapping).items()
        },
        column.name,
        kwargs.get("helper"),
    )
