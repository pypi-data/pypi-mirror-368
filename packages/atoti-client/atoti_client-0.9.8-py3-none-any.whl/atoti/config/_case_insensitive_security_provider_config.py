from typing import Literal
from warnings import warn

from pydantic.dataclasses import dataclass

from .._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CaseInsensitiveSecurityProviderConfig:  # pylint: disable=final-class
    username_case_conversion: Literal["upper", "lower", None] = None
    """The case conversion to apply to the username.

    This authentication provider is generally case insensitive: the same user :guilabel:`Jane` could log in with the usernames ``"jane"``, ``"Jane"``, ``"JANE"``, etc.
    This attribute allows reducing all the possible cases to a single one to be compatible with :attr:`~atoti.security.Security.individual_roles` and other case sensitive mappings.

    For instance, if ``session.security.individual_roles == {"jane": {"ROLE_USER"}}``, :attr:`username_case_conversion` should be set to ``"lower"``.

    Leaving this attribute to ``None`` is deprecated since it is a source of confusion or bugs.
    """

    def __post_init__(self) -> None:
        if self.username_case_conversion is None:
            warn(
                "Not selecting a `username_case_conversion` is deprecated.",
                category=_DEPRECATED_WARNING_CATEGORY,
                stacklevel=2,
            )
