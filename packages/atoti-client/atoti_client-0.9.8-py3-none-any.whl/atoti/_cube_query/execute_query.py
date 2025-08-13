from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Literal

import pandas as pd

from .._client import Client
from .._cube_discovery import get_discovery
from .._cube_query_filter_condition import CubeQueryFilterCondition
from .._generate_mdx import generate_mdx
from .._get_data_types import GetDataTypes
from .._identification import CubeIdentifier, LevelIdentifier, MeasureIdentifier
from .._mdx_query import Context, execute_query as execute_mdx_query
from .._session_id import SessionId
from .._typing import Duration
from ..mdx_query_result import MdxQueryResult


def execute_query(
    *,
    client: Client,
    context: Context,
    cube_identifier: CubeIdentifier,
    filter: CubeQueryFilterCondition | None,  # noqa: A002
    get_data_types: GetDataTypes,
    get_widget_creation_code: Callable[[], str | None],
    include_empty_rows: bool,
    include_totals: bool,
    level_identifiers: Sequence[LevelIdentifier],
    measure_identifiers: Sequence[MeasureIdentifier],
    mode: Literal["pretty", "raw"],
    scenario_name: str | None,
    session_id: SessionId,
    timeout: Duration,
) -> pd.DataFrame:
    discovery = get_discovery(client=client)

    mdx_ast = generate_mdx(
        cube=discovery.cubes[cube_identifier.cube_name],
        filter=filter,
        include_empty_rows=include_empty_rows,
        include_totals=include_totals,
        level_identifiers=level_identifiers,
        measure_identifiers=measure_identifiers,
        scenario=scenario_name,
    )
    mdx = str(mdx_ast)

    query_result = execute_mdx_query(
        mdx,
        client=client,
        context=context,
        get_data_types=get_data_types,
        get_discovery=lambda: discovery,
        get_widget_creation_code=get_widget_creation_code,
        keep_totals=include_totals,
        mode=mode,
        session_id=session_id,
        timeout=timeout,
    )

    if (
        # If totals were included, there is no need to change the existing widget conversion details.
        not include_totals
        and isinstance(query_result, MdxQueryResult)
        and query_result._atoti_metadata is not None
        and query_result._atoti_metadata.widget_conversion_details is not None
    ):
        mdx_ast = generate_mdx(
            cube=discovery.cubes[cube_identifier.cube_name],
            filter=filter,
            include_empty_rows=include_empty_rows,
            # Always use an MDX including totals because Atoti UI 5 relies only on context values to show/hide totals.
            include_totals=True,
            level_identifiers=level_identifiers,
            measure_identifiers=measure_identifiers,
            scenario=scenario_name,
        )
        mdx = str(mdx_ast)
        query_result._atoti_metadata = (
            query_result._atoti_metadata.add_widget_conversion_details(
                replace(
                    query_result._atoti_metadata.widget_conversion_details,
                    mdx=mdx,
                ),
            )
        )

    return query_result
