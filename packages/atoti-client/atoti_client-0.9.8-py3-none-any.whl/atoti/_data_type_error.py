from typing import final


@final
class DataTypeError(TypeError):
    """Error raised when a measure does not have the expected type."""
