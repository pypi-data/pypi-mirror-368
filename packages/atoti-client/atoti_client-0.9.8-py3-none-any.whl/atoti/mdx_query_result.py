from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, final

import pandas as pd
from typing_extensions import override

from ._mdx_query import Context
from ._mdx_query_result_metadata import MdxQueryResultMetadata
from ._mime_type import (
    HTML_MIME_TYPE as _HTML_MIME_TYPE,
    TEXT_MIME_TYPE as _TEXT_MIME_TYPE,
)
from ._widget_conversion_details import (
    CONVERT_MDX_QUERY_RESULT_TO_WIDGET_MIME_TYPE as _CONVERT_MDX_QUERY_RESULT_TO_WIDGET_MIME_TYPE,
)

if TYPE_CHECKING:
    # This requires pandas' optional dependency jinja2.
    from pandas.io.formats.style import Styler  # pylint: disable=nested-import

_METADATA_PROPERTY_NAME = "_atoti_metadata_"


@final
class MdxQueryResult(pd.DataFrame):
    """pandas DataFrame corresponding to the result of an MDX query ran in ``"pretty"`` *mode*.

    It is indexed by the queried levels (date levels become :class:`pandas.DatetimeIndex`).
    The rows are ordered according to the levels' :attr:`~atoti.Level.order`.

    .. note::
        Unless mutated in place, the ``__repr__()``, ``_repr_html_()``, ``_repr_latex_()``, and ``_repr_mimebundle_()`` methods will use:

        * The caption of levels and members instead of their name.
        * The formatted value of measures instead of their value.
    """

    # See https://pandas.pydata.org/pandas-docs/version/2.0/development/extending.html#define-original-properties
    _internal_names = [  # noqa: RUF012
        *pd.DataFrame._internal_names,  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
        _METADATA_PROPERTY_NAME,
    ]
    _internal_names_set = set(_internal_names)  # noqa: RUF012

    def __init__(
        self,
        # pandas does not expose the types of these arguments.
        data: Any = None,
        index: Any = None,
        *,
        context: Context | None = None,
        formatted_values: pd.DataFrame,
        get_styler: Callable[[], Styler],
    ):
        # `pandas-stub` declares a `__new__` but `pandas` actually have an `__init__`.
        super().__init__(data, index)  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]

        self._atoti_metadata = MdxQueryResultMetadata(
            context=context,
            formatted_values=formatted_values,
            get_styler=get_styler,
            initial_dataframe=self.copy(deep=True),
            widget_conversion_details=None,
        )

    # The conversion to an Atoti widget and the styling require this dataframe to be the original result of the MDX query.
    # If the dataframe was mutated, this property will be set to `None` to disable these features.
    @property
    def _atoti_metadata(self) -> MdxQueryResultMetadata | None:
        metadata = getattr(self, _METADATA_PROPERTY_NAME, None)

        if metadata is None:
            return None

        assert isinstance(metadata, MdxQueryResultMetadata)

        if not self.equals(metadata.initial_dataframe):
            del self._atoti_metadata
            return None

        return metadata

    @_atoti_metadata.setter
    def _atoti_metadata(self, value: MdxQueryResultMetadata, /) -> None:
        setattr(self, _METADATA_PROPERTY_NAME, value)

    @_atoti_metadata.deleter
    def _atoti_metadata(self) -> None:
        delattr(self, _METADATA_PROPERTY_NAME)

    @property
    @override
    def style(self) -> Styler:
        """Return a styler following the style included in the CellSet from which the DataFrame was converted (if it has not been mutated)."""
        return (
            self._atoti_metadata.get_styler() if self._atoti_metadata else super().style
        )

    @override
    def __repr__(self) -> str:
        return (
            repr(self._atoti_metadata.formatted_values)
            if self._atoti_metadata
            else super().__repr__()
        )

    @override  # `pandas-stubs` lacks the `_repr_html_` method.
    def _repr_html_(self) -> str | None:  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        html = (
            self._atoti_metadata.formatted_values._repr_html_()  # type: ignore[operator] # pyright: ignore[reportCallIssue]
            if self._atoti_metadata
            else super()._repr_html_()  # type: ignore[misc] # pyright: ignore[reportAttributeAccessIssue]
        )
        assert isinstance(html, type(None) | str)
        return html

    @override  # `pandas-stubs` lacks the `_repr_latex_` method.
    def _repr_latex_(self) -> str | None:  # type: ignore[misc]  # pyright: ignore[reportGeneralTypeIssues]
        latex = (
            self._atoti_metadata.formatted_values._repr_latex_()  # type: ignore[operator] # pyright: ignore[reportCallIssue]
            if self._atoti_metadata
            else super()._repr_latex_()  # type: ignore[misc] # pyright: ignore[reportAttributeAccessIssue]
        )
        assert isinstance(latex, type(None) | str)
        return latex

    @override  # `pandas-stubs` lacks the `_repr_mimebundle_` method.
    def _repr_mimebundle_(  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        self,
        include: object,
        exclude: object,
    ) -> dict[str, object]:
        mimebundle: dict[str, object] = {
            _HTML_MIME_TYPE: self._repr_html_(),
            _TEXT_MIME_TYPE: repr(self),
        }

        if self._atoti_metadata and self._atoti_metadata.widget_conversion_details:
            mimebundle[_CONVERT_MDX_QUERY_RESULT_TO_WIDGET_MIME_TYPE] = asdict(
                self._atoti_metadata.widget_conversion_details,
            )

        return mimebundle
