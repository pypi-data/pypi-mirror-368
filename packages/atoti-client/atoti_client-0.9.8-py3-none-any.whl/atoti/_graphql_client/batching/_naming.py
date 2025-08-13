_MERGED_NAME_SEPARATOR = "_"


def get_merged_name(name: str, /, *, index: int) -> str:
    return f"{name}{_MERGED_NAME_SEPARATOR}{index}"


def get_unmerged_name_and_index(merged_name: str, /) -> tuple[str, int]:
    name, index = merged_name.rsplit(_MERGED_NAME_SEPARATOR, maxsplit=1)
    return name, int(index)
