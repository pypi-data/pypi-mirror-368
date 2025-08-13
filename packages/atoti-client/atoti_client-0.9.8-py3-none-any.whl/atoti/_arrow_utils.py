from collections.abc import Mapping
from pathlib import Path

import pyarrow as pa

from ._data_type import DataType

_DATA_TYPE_FROM_ARROW_TYPE: Mapping[object, DataType] = {
    pa.bool_(): "boolean",
    pa.date32(): "LocalDate",
    pa.float32(): "float",
    pa.float64(): "double",
    pa.int32(): "int",
    pa.int64(): "long",
    pa.list_(pa.float32()): "float[]",
    pa.list_(pa.float64()): "double[]",
    pa.list_(pa.int32()): "int[]",
    pa.list_(pa.int64()): "long[]",
    pa.string(): "String",
    pa.timestamp("ns"): "LocalDateTime",
    pa.timestamp("s"): "LocalDateTime",
    pa.time64("ns"): "LocalTime",
    pa.null(): "String",
}

DEFAULT_MAX_CHUNKSIZE = 1_000


def write_arrow_to_file(
    table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
    /,
    *,
    max_chunksize: int = DEFAULT_MAX_CHUNKSIZE,
    filepath: Path,
) -> None:
    with pa.ipc.new_file(filepath, table.schema) as writer:
        for batch in table.to_batches(max_chunksize=max_chunksize):
            writer.write(batch)


def _get_data_type_from_arrow_type(arrow_type: object, /, *, name: str) -> DataType:
    if isinstance(arrow_type, pa.Decimal128Type | pa.Decimal256Type):
        return "double"

    try:
        return _DATA_TYPE_FROM_ARROW_TYPE[arrow_type]
    except KeyError as error:
        raise TypeError(f"`{name}` has unsupported type: `{arrow_type}`.") from error


def get_data_types_from_arrow(
    table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
    /,
) -> dict[str, DataType]:
    arrow_types = [
        arrow_type.value_type
        if isinstance(arrow_type, pa.DictionaryType)
        else arrow_type
        for arrow_type in table.schema.types
    ]
    return {
        table.column_names[i]: (
            "ZonedDateTime"
            if isinstance(arrow_type, pa.TimestampType) and arrow_type.tz is not None
            else _get_data_type_from_arrow_type(arrow_type, name=table.column_names[i])
        )
        for i, arrow_type in enumerate(arrow_types)
    }


def get_arrow_type(data_type: DataType, /) -> object | None:
    # Converting `ZonedDateTime` to an Arrow type is too complicated.
    # It will fall back to the type inferred by Arrow.
    if data_type == "ZonedDateTime":
        return None

    return next(
        arrow_type
        for arrow_type, arrow_data_type in _DATA_TYPE_FROM_ARROW_TYPE.items()
        if arrow_data_type == data_type
    )
