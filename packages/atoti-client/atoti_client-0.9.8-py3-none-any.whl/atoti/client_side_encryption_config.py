from abc import ABC

from pydantic.dataclasses import dataclass

from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ClientSideEncryptionConfig(ABC):  # noqa: B024
    """Config to load client-side encrypted files.

    The supported implementations are:

    * :class:`atoti_aws.KeyPair`
    * :class:`atoti_aws.KmsConfig`
    * :class:`atoti_azure.KeyPair`

    """
