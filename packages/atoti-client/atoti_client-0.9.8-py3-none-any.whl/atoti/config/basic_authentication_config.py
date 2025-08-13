from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class BasicAuthenticationConfig:
    """The `basic authentication <https://en.wikipedia.org/wiki/Basic_access_authentication>`__ config.

    It is the quickest way to set up security since it only requires defining :attr:`~atoti.security.basic_authentication_security.BasicAuthenticationSecurity.credentials` and :attr:`~atoti.security.Security.individual_roles`.

    See Also:
        :class:`atoti.BasicAuthentication`.
    """

    realm: str | None = None
    """The realm describing the protected area.

    Different realms can be used to isolate sessions running on the same domain (regardless of the port).

    When ``None``, a machine-wide unique ID will be used.
    """
