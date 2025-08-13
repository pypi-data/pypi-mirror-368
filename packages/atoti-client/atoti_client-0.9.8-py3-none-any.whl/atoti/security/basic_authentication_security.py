from __future__ import annotations

from collections.abc import MutableMapping
from typing import Final, final

from .._identification import UserName


@final
class BasicAuthenticationSecurity:
    """Manage Basic Authentication security on the session.

    Note:
        This requires :attr:`atoti.SessionConfig.security` to not be ``None``.
    """

    def __init__(self, *, credentials: MutableMapping[UserName, str]) -> None:
        self._credentials: Final = credentials

    @property
    def credentials(self) -> MutableMapping[UserName, str]:
        """Mapping from username to password.

        Use :attr:`~atoti.security.Security.individual_roles` to grant roles to the users.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> session = tt.Session.start(session_config)
            >>> session.security.basic_authentication.credentials
            {}

            Letting a user authenticate through Basic Authentication requires two steps:

            * Granting the required role:

              >>> session.security.individual_roles["Chen"] = {"ROLE_USER"}

            * Configuring credentials:

              >>> session.security.basic_authentication.credentials["Chen"] = "Peking"

            The password can be changed:

            >>> session.security.basic_authentication.credentials["Chen"] = "Beijing"

            But, for security reasons, it cannot be retrieved.
            Accessing it will return a redacted string:

            >>> session.security.basic_authentication.credentials
            {'Chen': '**REDACTED**'}

            Revoking access:

            >>> del session.security.basic_authentication.credentials["Chen"]
            >>> session.security.basic_authentication.credentials
            {}

            Cleaning the individual roles to not leave unused keys:

            >>> del session.security.individual_roles["Chen"]

            .. doctest::
                :hide:

                >>> del session
        """
        return self._credentials
