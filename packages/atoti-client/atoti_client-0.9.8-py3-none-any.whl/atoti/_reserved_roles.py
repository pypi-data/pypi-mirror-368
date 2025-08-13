from collections.abc import Collection

from ._identification import Role

ROLE_ADMIN: Role = "ROLE_ADMIN"
ROLE_ANONYMOUS: Role = "ROLE_ANONYMOUS"
ROLE_USER: Role = "ROLE_USER"

_RESERVED_ROLES: Collection[Role] = (ROLE_ADMIN, ROLE_ANONYMOUS, ROLE_USER)


def check_no_reserved_roles(role_names: Collection[Role]) -> None:
    for role in role_names:
        if role in _RESERVED_ROLES:
            raise ValueError(f"Role `{role}` is reserved, use another role.")
