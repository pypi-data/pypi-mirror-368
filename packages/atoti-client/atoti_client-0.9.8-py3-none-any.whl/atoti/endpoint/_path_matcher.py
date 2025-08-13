import re
from io import StringIO
from typing import Final, final


@final
class PathMatcher:
    def __init__(self, template: str, /):
        self._parameter_names: Final[list[str]] = []

        pattern_writer = StringIO("^")

        # None when current character not between braces.
        parameter_name_start_index: int | None = None

        for index, character in enumerate(template):
            match character, parameter_name_start_index:
                case "{", int():
                    raise ValueError(f"Found nested {{ at index {index}.")
                case "{", None:
                    parameter_name_start_index = index
                case "}", int(parameter_name_start_index):
                    parameter_name = template[parameter_name_start_index + 1 : index]
                    if parameter_name in self._parameter_names:
                        raise ValueError(f"Duplicate parameter `{parameter_name}`.")

                    self._parameter_names.append(parameter_name)
                    pattern_writer.write(r"([^/]+)")
                    parameter_name_start_index = None
                case "}", None:
                    raise ValueError(f"}} at index {index} has no matching {{.")
                case str(), int():
                    ...
                case str(), None:
                    pattern_writer.write(re.escape(character))

        if parameter_name_start_index is not None:
            raise ValueError(
                f"{{ at index {parameter_name_start_index} has no matching }}."
            )

        pattern_writer.write("$")
        self._pattern: Final = re.compile(pattern_writer.getvalue())

    def get_parameters(self, path: str, /) -> dict[str, str] | None:
        match = self._pattern.match(path)
        if match is None:
            return None
        groups = match.groups()
        return dict(zip(self._parameter_names, groups, strict=True))
