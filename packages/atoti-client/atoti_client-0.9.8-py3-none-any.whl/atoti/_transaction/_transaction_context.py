from typing import TypeVar

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .transaction_id import TransactionId


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
# Not `@final` because inherited by `DataTransactionContext` and `DataModelTransactionContext`.
class TransactionContext:  # pylint: disable=final-class
    transaction_id: TransactionId


TransactionContextT = TypeVar("TransactionContextT", bound=TransactionContext)
