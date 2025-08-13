from collections.abc import Callable
from typing import Literal, overload

import pandas as pd

from .._cellset_to_mdx_query_result import cellset_to_mdx_query_result
from .._client import Client
from .._cube_discovery import Discovery
from .._get_data_types import GetDataTypes
from .._pandas import pandas_from_arrow
from .._session_id import SessionId
from .._typing import Duration
from .._widget_conversion_details import WidgetConversionDetails
from ..mdx_query_result import MdxQueryResult
from ._enrich_context import enrich_context
from ._execute_query_to_arrow_table import execute_query_to_arrow_table
from ._execute_query_to_cellset import execute_query_to_cellset
from .context import Context


@overload
def execute_query(
    mdx: str,
    /,
    *,
    client: Client,
    context: Context,
    get_data_types: GetDataTypes | None,
    get_discovery: Callable[[], Discovery],
    get_widget_creation_code: Callable[[], str | None],
    keep_totals: bool,
    mode: Literal["pretty"],
    session_id: SessionId,
    timeout: Duration,
) -> MdxQueryResult: ...


@overload
def execute_query(
    mdx: str,
    /,
    *,
    client: Client,
    context: Context,
    get_data_types: GetDataTypes | None,
    get_discovery: Callable[[], Discovery],
    get_widget_creation_code: Callable[[], str | None],
    keep_totals: bool,
    mode: Literal["raw"],
    session_id: SessionId,
    timeout: Duration,
) -> pd.DataFrame: ...


def execute_query(
    mdx: str,
    /,
    *,
    client: Client,
    context: Context,
    get_data_types: GetDataTypes | None,
    get_discovery: Callable[[], Discovery],
    get_widget_creation_code: Callable[[], str | None],
    keep_totals: bool,
    mode: Literal["pretty", "raw"],
    session_id: SessionId,
    timeout: Duration,
) -> MdxQueryResult | pd.DataFrame:
    context = enrich_context(context, timeout=timeout)

    if mode == "raw":
        arrow_table = execute_query_to_arrow_table(mdx, client=client, context=context)
        return pandas_from_arrow(arrow_table)

    cellset = execute_query_to_cellset(mdx, client=client, context=context)
    cube_discovery = get_discovery()
    query_result = cellset_to_mdx_query_result(
        cellset,
        context=context,
        cube=cube_discovery.cubes[cellset.cube],
        get_data_types=get_data_types,
        keep_totals=keep_totals,
    )

    widget_creation_code = get_widget_creation_code()
    if widget_creation_code is not None and query_result._atoti_metadata is not None:
        query_result._atoti_metadata = (
            query_result._atoti_metadata.add_widget_conversion_details(
                WidgetConversionDetails(
                    mdx=mdx,
                    sessionId=session_id,
                    widgetCreationCode=widget_creation_code,
                ),
            )
        )

    return query_result
