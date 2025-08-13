from collections import defaultdict
from collections.abc import Mapping

from ._naming import get_unmerged_name_and_index


def unmerge_output(
    output: Mapping[str, object], /, *, document_count: int
) -> list[Mapping[str, object]]:
    match document_count:
        case 0 | 1:
            return [output]
        case _:
            outputs: dict[int, dict[str, object]] = defaultdict(dict)
            for merged_name, value in output.items():
                name, index = get_unmerged_name_and_index(merged_name)
                outputs[index][name] = value
            return list(outputs.values())
