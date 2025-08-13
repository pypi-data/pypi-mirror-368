from ._constant import json_from_constant
from ._operation import (
    MembershipCondition,
    RelationalCondition,
    dnf_from_condition,
)
from ._table_query_filter_condition import TableQueryFilterCondition

_AndDict = dict[
    str,
    dict[str, object | list[object]],
]

_OrDict = dict[str, list[_AndDict]]

_JsonSerializableDict = dict[str, list[_OrDict]]


def json_serializable_dict_from_condition(  # noqa: C901
    condition: TableQueryFilterCondition,
    /,
) -> _JsonSerializableDict:
    or_dicts: list[_OrDict] = []

    for conjunct_conditions in dnf_from_condition(condition):
        and_list: list[_AndDict] = []

        for leaf_condition in conjunct_conditions:
            match leaf_condition:
                case MembershipCondition(subject=subject, operator=operator):
                    and_list.append(
                        {
                            subject.column_name: {  # type: ignore[attr-defined]
                                "$in": [
                                    json_from_constant(element)  # type: ignore[arg-type]
                                    for element in leaf_condition._sorted_elements
                                ],
                            },
                        }
                    )
                case RelationalCondition(
                    subject=subject, operator=operator, target=target
                ):
                    match operator:
                        case "==" | ">=" | ">" | "<=" | "<":
                            match operator:
                                case "==":
                                    _operator: str = "eq"
                                case ">=":
                                    _operator = "gte"
                                case ">":
                                    _operator = "gt"
                                case "<=":
                                    _operator = "lte"
                                case "<":
                                    _operator = "lt"

                            and_list.append(
                                {
                                    subject.column_name: {  # type: ignore[union-attr]
                                        f"${_operator}": json_from_constant(
                                            leaf_condition.target  # type: ignore[arg-type]
                                        ),
                                    },
                                },
                            )
                        case "!=":
                            and_list.append(
                                {
                                    "$not": {
                                        subject.column_name: json_from_constant(target),  # type: ignore[arg-type,union-attr]
                                    },
                                },
                            )

        or_dicts.append({"$and": and_list})

    return {"$or": or_dicts}
