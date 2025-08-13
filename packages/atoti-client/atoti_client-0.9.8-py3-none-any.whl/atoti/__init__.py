from . import (
    agg as agg,
    array as array,
    finance as finance,
    function as function,
    math as math,
    stats as stats,
    string as string,
)
from ._compose_decorators import compose_decorators as _compose_decorators
from ._data_type import DataType as DataType
from ._decorate_api import decorate_api as _decorate_api
from ._disable_call_validation_env_var_name import (
    DISBALE_CALL_VALIDATION_ENV_VAR_NAME as _DISBALE_CALL_VALIDATION_ENV_VAR_NAME,
)
from ._env import get_env_flag as _get_env_flag
from ._eula import (
    EULA as __license__,  # noqa: N811, F401
    hide_new_eula_message as hide_new_eula_message,
    print_eula_message as _print_eula_message,
)
from ._py4j_client._utils import patch_databricks_py4j as _patch_databricks_py4j
from ._telemetry import telemeter as _telemeter
from ._validate_call import validate_call as __validate_call
from .aggregate_cache import AggregateCache as AggregateCache
from .aggregate_provider import AggregateProvider as AggregateProvider
from .app_extension import ADVANCED_APP_EXTENSION as ADVANCED_APP_EXTENSION
from .authentication import *
from .client_side_encryption_config import (
    ClientSideEncryptionConfig as ClientSideEncryptionConfig,
)
from .cluster_definition import ClusterDefinition as ClusterDefinition
from .column import Column as Column
from .config import *
from .cube import Cube as Cube
from .data_load import CsvLoad as CsvLoad, ParquetLoad as ParquetLoad
from .directquery import *
from .distribution import *
from .distribution_protocols import *
from .experimental import experimental as experimental
from .function import *
from .hierarchy import Hierarchy as Hierarchy
from .key_pair import KeyPair as KeyPair
from .level import Level as Level
from .mapping_lookup import mapping_lookup as mapping_lookup
from .mdx_query_result import MdxQueryResult as MdxQueryResult
from .measure import Measure as Measure
from .order import *
from .scope import *
from .session import Session as Session
from .table import Table as Table
from .type import *
from .user import User as User

_print_eula_message()

_patch_databricks_py4j()

_track_call = _telemeter()
_validate_call = (
    __validate_call
    if __debug__ and not _get_env_flag(_DISBALE_CALL_VALIDATION_ENV_VAR_NAME)
    else None
)
_api_decorators = tuple(
    decorator for decorator in [_track_call, _validate_call] if decorator is not None
)
if _api_decorators:
    _decorate_api(_compose_decorators(*_api_decorators))
