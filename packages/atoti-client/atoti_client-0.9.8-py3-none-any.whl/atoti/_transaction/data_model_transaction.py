from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from contextvars import ContextVar
from typing import final

from pydantic.dataclasses import dataclass

from .._collections import frozendict
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .._session_id import SessionId
from ._get_transaction_id import get_transaction_id
from ._transact import transact
from ._transaction_context import TransactionContext
from .transaction_id import TransactionId


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class DataModelTransactionContext(TransactionContext): ...


_CONTEXT_VAR: ContextVar[Mapping[SessionId, DataModelTransactionContext]] = ContextVar(
    "atoti_data_model_transaction", default=frozendict()
)


def get_data_model_transaction_id(session_id: SessionId, /) -> TransactionId | None:
    return get_transaction_id(_CONTEXT_VAR, session_id)


def _create_context(transaction_id: TransactionId, /) -> DataModelTransactionContext:
    return DataModelTransactionContext(transaction_id=transaction_id)


def _rollback(
    transaction_id: TransactionId,
) -> None:
    # Rollback of data model transactions is not supported yet.
    ...


def _start() -> str:
    # In the future, Atoti Server will be aware of the data model transaction and provide its ID to the client.
    return "unused"


def transact_data_model(
    *,
    allow_nested: bool,
    commit: Callable[..., None],
    session_id: SessionId,
) -> AbstractContextManager[None]:
    return transact(
        allow_nested=allow_nested,
        commit=lambda _: commit(),
        context_var=_CONTEXT_VAR,
        create_context=_create_context,
        rollback=_rollback,
        session_id=session_id,
        start=_start,
    )
