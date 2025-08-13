from collections.abc import Mapping, Sequence

from ._naming import get_merged_name


def merge_variables(
    all_variables: Sequence[Mapping[str, object]], /
) -> Mapping[str, object]:
    match all_variables:
        case []:
            return {}
        case [variables]:
            return variables
        case _:
            return {
                get_merged_name(name, index=index): value
                for index, variables in enumerate(all_variables)
                for name, value in variables.items()
            }
