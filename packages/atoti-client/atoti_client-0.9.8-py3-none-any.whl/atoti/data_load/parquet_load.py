from dataclasses import KW_ONLY
from pathlib import Path
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._collections import FrozenMapping, frozendict
from .._identification import ColumnName
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, get_type_adapter
from ..client_side_encryption_config import ClientSideEncryptionConfig
from .data_load import DataLoad


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ParquetLoad(DataLoad):
    """The definition of an Apache Parquet file load.

    See Also:
        The other :class:`~atoti.data_load.DataLoad` implementations.
    """

    path: Path | str
    """The path to the Parquet file.

    If a path pointing to a directory is provided, all of the files with the ``.parquet`` extension in the directory will be loaded into the same table and, as such, they are all expected to share the same schema.

    The path can also be a glob pattern (e.g. ``"path/to/directory/*.parquet"``).
    """

    _: KW_ONLY

    client_side_encryption: ClientSideEncryptionConfig | None = None

    columns: FrozenMapping[str, ColumnName] = frozendict()
    """Mapping from file column names to table column names.

    When the mapping is not empty, columns of the file absent from the mapping keys will not be loaded.
    Other parameters accepting column names expect to be passed table column names (i.e. values of this mapping) and not file column names."""

    @property
    @override
    def _options(
        self,
    ) -> dict[str, object]:
        path = str(self.path) if isinstance(self.path, Path) else self.path
        return {
            "clientSideEncryptionConfig": get_type_adapter(
                type(self.client_side_encryption),
            ).dump_python(self.client_side_encryption)
            if self.client_side_encryption is not None
            else None,
            "columns": self.columns,
            "path": path,
        }

    @property
    @override
    def _plugin_key(self) -> str:
        return "PARQUET"
