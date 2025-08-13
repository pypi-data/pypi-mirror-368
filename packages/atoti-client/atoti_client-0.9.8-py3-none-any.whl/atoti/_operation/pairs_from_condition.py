from typing import Literal

from .dnf_from_condition import (
    dnf_from_condition,
)
from .operation import (
    LogicalCondition,
    RelationalCondition,
    RelationalConditionSubjectT_co,
    RelationalConditionTargetT_co,
)


def pairs_from_condition(
    condition: RelationalCondition[
        RelationalConditionSubjectT_co,
        Literal["=="],
        RelationalConditionTargetT_co,
    ]
    | LogicalCondition[
        RelationalCondition[
            RelationalConditionSubjectT_co,
            Literal["=="],
            RelationalConditionTargetT_co,
        ],
        Literal["&"],
    ],
    /,
) -> list[tuple[RelationalConditionSubjectT_co, RelationalConditionTargetT_co]]:
    dnf: tuple[
        tuple[
            RelationalCondition[
                RelationalConditionSubjectT_co,
                Literal["=="],
                RelationalConditionTargetT_co,
            ],
            ...,
        ]
    ] = dnf_from_condition(condition)
    (conjunct_conditions,) = dnf
    return [(condition.subject, condition.target) for condition in conjunct_conditions]
