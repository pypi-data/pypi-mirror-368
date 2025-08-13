import os

from .._pydantic import get_type_adapter


def get_env_flag(variable_name: str, /) -> bool:
    adapter = get_type_adapter(bool)
    return adapter.validate_python(
        os.environ.get(
            variable_name,
            # The default is not configurable because it's simpler if `absence of the flag <=> the flag is false`.
            str(False),
        ),
    )
