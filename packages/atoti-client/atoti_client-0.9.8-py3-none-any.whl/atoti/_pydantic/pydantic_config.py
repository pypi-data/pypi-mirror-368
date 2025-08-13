from pydantic import ConfigDict

PYDANTIC_CONFIG: ConfigDict = {
    "arbitrary_types_allowed": True,
    "extra": "forbid",  # Consistent with the standard library dataclasses.
    "serialize_by_alias": True,
    "validate_default": True,
}
