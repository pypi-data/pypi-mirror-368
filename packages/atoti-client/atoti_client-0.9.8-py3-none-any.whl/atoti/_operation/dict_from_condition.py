from typing import Literal

from .._identification import IdentifierT_co
from .operation import (
    LogicalCondition,
    RelationalCondition,
    RelationalConditionTargetT_co,
)
from .pairs_from_condition import pairs_from_condition


def dict_from_condition(
    condition: RelationalCondition[
        IdentifierT_co,
        Literal["=="],
        RelationalConditionTargetT_co,
    ]
    | LogicalCondition[
        RelationalCondition[
            IdentifierT_co,
            Literal["=="],
            RelationalConditionTargetT_co,
        ],
        Literal["&"],
    ],
    /,
) -> dict[IdentifierT_co, RelationalConditionTargetT_co]:
    pairs = pairs_from_condition(condition)
    result: dict[IdentifierT_co, RelationalConditionTargetT_co] = {}

    for identifier, target in pairs:
        if identifier in result:
            raise ValueError(
                f"Expected the combined condition to have distinct subjects but got `{identifier}` twice.",
            )

        result[identifier] = target

    return result
