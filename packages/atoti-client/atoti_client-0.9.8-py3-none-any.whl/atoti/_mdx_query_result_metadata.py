from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Final, final

import pandas as pd

from ._mdx_query import Context
from ._widget_conversion_details import WidgetConversionDetails

if TYPE_CHECKING:
    # This requires pandas' optional dependency jinja2.
    from pandas.io.formats.style import Styler  # pylint: disable=nested-import


@final
class MdxQueryResultMetadata:
    def __init__(
        self,
        *,
        context: Context | None,
        formatted_values: pd.DataFrame,
        get_styler: Callable[[], Styler],
        initial_dataframe: pd.DataFrame,
        widget_conversion_details: WidgetConversionDetails | None,
    ) -> None:
        self.context: Final = context
        self.formatted_values: Final = formatted_values
        self.get_styler: Final = get_styler
        self.initial_dataframe: Final = initial_dataframe
        self.widget_conversion_details: Final = widget_conversion_details

    def add_widget_conversion_details(
        self,
        widget_conversion_details: WidgetConversionDetails,
        /,
    ) -> MdxQueryResultMetadata:
        return MdxQueryResultMetadata(
            context=self.context,
            formatted_values=self.formatted_values,
            get_styler=self.get_styler,
            initial_dataframe=self.initial_dataframe,
            widget_conversion_details=widget_conversion_details,
        )
