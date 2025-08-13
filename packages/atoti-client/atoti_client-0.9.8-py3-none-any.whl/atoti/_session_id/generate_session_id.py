from random import choices
from string import digits
from time import time

from .session_id import SessionId


def generate_session_id() -> SessionId:
    random_string = "".join(
        # No cryptographic security required.
        choices(digits, k=6),  # noqa: S311
    )
    return SessionId(f"{int(time())}_{random_string}")
