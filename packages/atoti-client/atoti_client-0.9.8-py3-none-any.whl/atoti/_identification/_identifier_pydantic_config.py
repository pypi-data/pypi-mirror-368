from pydantic import ConfigDict

from .._pydantic import PYDANTIC_CONFIG

IDENTIFIER_PYDANTIC_CONFIG: ConfigDict = {
    **PYDANTIC_CONFIG,
    "arbitrary_types_allowed": False,
}
