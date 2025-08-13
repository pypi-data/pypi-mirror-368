from dataclasses import KW_ONLY
from typing import Literal, final

from pydantic.dataclasses import dataclass

from .._constant import Constant
from .._identification import ColumnIdentifier, Identifiable, TableIdentifier
from .._operation import (
    EqualityOperator,
    LogicalCondition,
    LogicalOperator,
    MembershipCondition,
    RelationalCondition,
)
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG

_ExternalTableUpdateChangeType = Literal["add", "remove", "update", "mixed", "infer"]

_ExternalTableUpdatePerimeterLeafCondition = (
    MembershipCondition[ColumnIdentifier, Literal["in"], Constant]
    | RelationalCondition[ColumnIdentifier, EqualityOperator, Constant]
)
_ExternalTableUpdatePerimeterCondition = (
    _ExternalTableUpdatePerimeterLeafCondition
    | LogicalCondition[_ExternalTableUpdatePerimeterLeafCondition, LogicalOperator]
)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ExternalTableUpdate:
    """The definition of an update that occurred on an external table.

    It is used to compute the smallest incremental refresh possible.
    """

    table: Identifiable[TableIdentifier]
    """The table on which the update occurred."""

    _: KW_ONLY

    change_type: _ExternalTableUpdateChangeType = "mixed"
    """The type of change that occurred:

    * ``"add"``: Some rows have been added.
    * ``"update"``: Some rows have been updated (e.g. the values of some non key columns changed).
      The updated columns cannot be used in *perimeter*.
    * ``"remove"``: Some rows have been removed.
    * ``"mixed"``: Some rows have been added, updated, or removed.
      If updated columns are used in *perimeter*, the condition must cover both previous and new values.
    * ``"infer"``: Some rows have been added to this *table* and the one it is joined to (declared in another ``TableUpdate``).
      This can be used when *table* is the target of a :meth:`~atoti.Table.join` created with ``target_optionality="mandatory"``.
      When that is the case, the added rows on this target *table* can be inferred from the *perimeter* of the ``TableUpdate`` (with *change_type* set to ``"add"``) of the source table.
      The row location information for this *table* is thus not required to perform an efficient incremental refresh.

    """

    perimeter: _ExternalTableUpdatePerimeterCondition | None = None
    """The condition describing the perimeter of the changed rows.

    * If ``None`` and *change_type* is different than ``"infer"`, all rows are considered to have changed.
    * If not ``None``, the condition must evaluate to ``True`` for all the changed rows and to ``False`` everywhere else.
    """

    def __post_init__(self) -> None:
        if self.change_type == "infer" and self.perimeter is not None:
            raise ValueError(
                "Cannot specify a perimeter when inferring the change type.",
            )
