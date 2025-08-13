import json
from collections import defaultdict
from collections.abc import Callable
from operator import attrgetter

from ._resources_directory import RESOURCES_DIRECTORY

_API_JSON_SNAPSHOT_PATH = RESOURCES_DIRECTORY / "api.json"

_ApiSnapshot = dict[str, dict[str, list[str]]]

_FUNCTION_TO_RE_EXPORTED_PATH: dict[str, dict[str, str]] = defaultdict(dict)


def decorate_api(
    decorator: Callable[[Callable[..., object]], Callable[..., object]], /
) -> None:
    api_snapshot: _ApiSnapshot = json.loads(_API_JSON_SNAPSHOT_PATH.read_bytes())

    for module_name, path_in_module_to_function_names in api_snapshot.items():
        module: object

        try:
            module = __import__(module_name)
        except ModuleNotFoundError:
            # Can happen when trying to decorate the API of a plugin that is not installed.
            continue

        for (
            path_in_module,
            function_names,
        ) in path_in_module_to_function_names.items():
            container = attrgetter(path_in_module)(module) if path_in_module else module
            for function_name in function_names:
                function = getattr(container, function_name)
                assert callable(function)
                _FUNCTION_TO_RE_EXPORTED_PATH[function.__module__][
                    function.__qualname__
                ] = f"""{module_name}.{f"{path_in_module}." if path_in_module else ""}{function_name}"""
                try:
                    decorated_function = decorator(function)
                    setattr(container, function_name, decorated_function)
                except Exception as error:
                    raise RuntimeError(f"Failed to decorate `{function}`.") from error


def get_function_re_exported_path(module_name: str, qualname: str, /) -> str:
    return _FUNCTION_TO_RE_EXPORTED_PATH[module_name][qualname]
