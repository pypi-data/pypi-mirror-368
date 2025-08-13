from ._data_type import (
    BooleanDataType as _BooleanDataType,
    DoubleArrayDataType as _DoubleArrayDataType,
    DoubleDataType as _DoubleDataType,
    FloatArrayDataType as _FloatArrayDataType,
    FloatDataType as _FloatDataType,
    IntArrayDataType as _IntArrayDataType,
    IntDataType as _IntDataType,
    LocalDateDataType as _LocalDateDataType,
    LocalDateTimeDataType as _LocalDateTimeDataType,
    LocalTimeDataType as _LocalTimeDataType,
    LongArrayDataType as _LongArrayDataType,
    LongDataType as _LongDataType,
    StringDataType as _StringDataType,
    ZonedDateTimeDataType as _ZonedDateTimeDataType,
)

BOOLEAN: _BooleanDataType = "boolean"
"""Boolean data type."""

DOUBLE: _DoubleDataType = "double"
"""Double data type."""

DOUBLE_ARRAY: _DoubleArrayDataType = "double[]"
"""Double array data type."""

FLOAT: _FloatDataType = "float"
"""Float data type."""

FLOAT_ARRAY: _FloatArrayDataType = "float[]"
"""Float array data type."""

INT: _IntDataType = "int"
"""Int data type."""

INT_ARRAY: _IntArrayDataType = "int[]"
"""Int array data type."""

LOCAL_DATE: _LocalDateDataType = "LocalDate"
"""LocalDate data type."""

LOCAL_DATE_TIME: _LocalDateTimeDataType = "LocalDateTime"
"""LocalDateTime data type."""

LOCAL_TIME: _LocalTimeDataType = "LocalTime"
"""LocalTime data type."""

LONG: _LongDataType = "long"
"""Long data type."""

LONG_ARRAY: _LongArrayDataType = "long[]"
"""Long array data type."""

STRING: _StringDataType = "String"
"""String data type."""

ZONED_DATE_TIME: _ZonedDateTimeDataType = "ZonedDateTime"
"""ZonedDateTime data type."""
