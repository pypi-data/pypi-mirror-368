from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DataLoad(ABC):
    """The definition of data that can be loaded into a table.

    The available implementations are:

    * :class:`atoti.CsvLoad`
    * :class:`atoti.ParquetLoad`
    * :class:`atoti_jdbc.JdbcLoad`

    See Also:
        :meth:`~atoti.Table.load` and :meth:`~atoti.tables.Tables.infer_data_types`.

    """

    @property
    @abstractmethod
    def _options(self) -> dict[str, object]: ...

    @property
    @abstractmethod
    def _plugin_key(self) -> str: ...
