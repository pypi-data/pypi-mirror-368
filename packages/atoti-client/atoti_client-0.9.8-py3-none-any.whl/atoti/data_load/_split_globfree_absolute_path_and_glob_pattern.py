from pathlib import Path

from pydantic import AnyUrl, ValidationError

from .._pydantic import get_type_adapter


def _is_absolute(path: str, /) -> bool:
    if Path(path).is_absolute():
        return True

    try:
        get_type_adapter(AnyUrl).validate_python(path)
    except ValidationError:
        return False
    else:
        return True


def _validate_glob_pattern(pattern: str, /) -> str:
    """Check the pattern meets our requirements and modify it if necessary."""
    pattern = pattern.replace("\\", "/")

    if ":" in pattern:
        split = pattern.split(":")
        if split[0] != "glob":
            raise ValueError("Only glob patterns are supported.")
        if split[1][0] == "/":
            # glob pattern does not need leading /
            split[1] = split[1][1:]
        return ":".join(split)

    if pattern[0] == "/":
        # glob pattern does not need leading /
        pattern = pattern[1:]

    return f"glob:{pattern}"


def split_globfree_absolute_path_and_glob_pattern(
    path: str | Path,
    /,
    *,
    extension: str,
) -> tuple[str, str | None]:
    input_is_path_instance = isinstance(path, Path)
    path = str(path)

    # Start by searching for glob characters in the string
    star_index = path.find("*")
    question_index = path.find("?")
    bracket_index = path.find("[") if path.find("]") > -1 else -1
    curly_index = path.find("{") if path.find("}") > -1 else -1

    glob_pattern_start_index = min(
        index
        for index in [len(path), star_index, question_index, bracket_index, curly_index]
        if index != -1
    )

    if glob_pattern_start_index == len(path):
        if not _is_absolute(path):
            path = str(Path(path).absolute())

        if path.endswith(extension) or (
            (extension == ".csv") and (path.endswith((".zip", ".tar.gz", ".gz")))
        ):
            return path, None

        if extension == ".parquet" and not path.endswith(extension):
            # To support reading directories containing partitioned Parquet files.
            return path, f"glob:*{extension}"

        raise ValueError(
            "Paths pointing to a directory are not supported, use a glob pattern instead.",
        )

    if input_is_path_instance:
        raise ValueError(
            "`Path` instance should not contain glob pattern, pass a `str` instead.",
        )

    last_separator_before_glob_pattern_index = next(
        index
        for index, character in reversed(list(enumerate(path)))
        if character in {"/", "\\"} and index < glob_pattern_start_index
    )

    globfree_path = path[:last_separator_before_glob_pattern_index]
    for glob_character in ["*", "?", "[", "{"]:
        assert glob_character not in globfree_path
    globfree_absolute_path = (
        globfree_path
        if _is_absolute(globfree_path)
        else str(Path(globfree_path).absolute())
    )

    glob_pattern = _validate_glob_pattern(
        path[last_separator_before_glob_pattern_index:],
    )

    return globfree_absolute_path, glob_pattern
