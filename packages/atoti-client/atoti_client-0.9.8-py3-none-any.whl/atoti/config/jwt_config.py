from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ..key_pair import KeyPair


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class JwtConfig:
    """The JWT config.

    Atoti uses JSON Web Tokens to authenticate requests between its components (e.g. between the app running in the browser and the session).
    """

    key_pair: KeyPair | None = None
    """The key pair used to sign the JWT.

    If ``None``, a random 3072-bit key pair will be generated when the session starts.

    Only RSA keys using the PKCS 8 standard are supported.
    Key pairs can be generated using a library such as `pycryptodome <https://www.pycryptodome.org/src/examples#generate-public-key-and-private-key>`__.
    """
