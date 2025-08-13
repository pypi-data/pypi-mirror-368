from collections.abc import Callable
from pathlib import Path
from typing import Annotated, final

from pydantic import AfterValidator, Field, FilePath
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


def _create_suffix_checker(
    expected_suffix: str,
    /,
) -> Callable[[Path], Path]:
    def _check_suffix(path: Path, /) -> Path:
        suffix = Path(path).suffix

        if suffix != expected_suffix:
            raise ValueError(
                f"Expected a {expected_suffix} file but got a {suffix} file.",
            )

        return path

    return _check_suffix


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class BrandingConfig:
    """The UI elements to :ref:`customize the app <guides/customizing_the_app:Branding>` by replacing the Atoti branding with another one (also called white-labeling).

    Note:
        This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.

    When defined, the :guilabel:`By ActiveViam` signature at the bottom right corner of the app will be removed.

    Example:
        >>> from pathlib import Path
        >>> config = tt.BrandingConfig(
        ...     favicon=TEST_RESOURCES_PATH / "config" / "branding" / "favicon.ico",
        ...     logo=TEST_RESOURCES_PATH / "config" / "branding" / "logo.svg",
        ...     title="Custom title",
        ... )

    """

    favicon: (
        Annotated[FilePath, AfterValidator(_create_suffix_checker(".ico"))] | None
    ) = None
    """The file path to a ``.ico`` image that will be used as the favicon."""

    logo: Annotated[FilePath, AfterValidator(_create_suffix_checker(".svg"))] | None = (
        None
    )
    """The file path to a 20px high ``.svg`` image that will be displayed in the upper-left corner."""

    dark_theme_logo: (
        Annotated[FilePath, AfterValidator(_create_suffix_checker(".svg"))] | None
    ) = None
    """The logo displayed in dark theme.

    If ``None``, :attr:`logo` will be used as a fallback (if it is not ``None`` itself).
    """

    title: Annotated[
        str,
        Field(
            exclude=True,  # Not sent to the server since it is handled client side.
        ),
    ] = "Atoti"
    """The title to give to the browser tab (in the home page)."""
