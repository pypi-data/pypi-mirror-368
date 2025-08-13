from collections.abc import Mapping
from typing import Any, cast

from .get_ipython import get_ipython


def find_corresponding_top_level_variable_name(
    value: object,
    /,
) -> str | None:
    ipython = get_ipython()

    if ipython is None:
        return None

    top_level_variables: Mapping[str, object] = cast(Any, ipython).user_ns

    for variable_name, variable_value in top_level_variables.items():
        is_regular_variable = not variable_name.startswith("_")
        if is_regular_variable and variable_value is value:
            return variable_name

    return None
