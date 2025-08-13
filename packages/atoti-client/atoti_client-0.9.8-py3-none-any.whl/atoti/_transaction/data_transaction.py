from __future__ import annotations

from collections.abc import Callable, Mapping, Set as AbstractSet
from contextlib import AbstractContextManager
from contextvars import ContextVar
from typing import Annotated, TypeAlias, final

from pydantic import Field
from pydantic.dataclasses import dataclass

from .._collections import frozendict
from .._identification import TableIdentifier
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .._session_id import SessionId
from ._get_transaction_id import get_transaction_id
from ._transact import transact
from ._transaction_context import TransactionContext
from .transaction_id import TransactionId

DataTransactionTableIdentifiers: TypeAlias = Annotated[
    AbstractSet[TableIdentifier], Field(min_length=1)
]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class DataTransactionContext(TransactionContext):
    table_identifiers: DataTransactionTableIdentifiers | None


_CONTEXT_VAR: ContextVar[Mapping[SessionId, DataTransactionContext]] = ContextVar(
    "atoti_data_transaction", default=frozendict()
)


def get_data_transaction_id(session_id: SessionId, /) -> TransactionId | None:
    return get_transaction_id(_CONTEXT_VAR, session_id)


def transact_data(
    *,
    allow_nested: bool,
    commit: Callable[[TransactionId], None],
    rollback: Callable[[TransactionId], None],
    session_id: SessionId,
    start: Callable[[], str],
    table_identifiers: DataTransactionTableIdentifiers | None,
) -> AbstractContextManager[None]:
    def check_nesting(previous_context: DataTransactionContext, /) -> None:
        if previous_context.table_identifiers is None:
            return

        if table_identifiers is None:
            raise RuntimeError(
                f"Cannot start a transaction locking all tables inside another transaction locking a subset of tables: {set(previous_context.table_identifiers)}.",
            )

        if not (table_identifiers <= previous_context.table_identifiers):
            raise RuntimeError(
                f"Cannot start a transaction locking tables {table_identifiers} inside another transaction locking tables {set(previous_context.table_identifiers)} which is not a superset.",
            )

    def create_context(transaction_id: TransactionId, /) -> DataTransactionContext:
        return DataTransactionContext(
            table_identifiers=table_identifiers,
            transaction_id=transaction_id,
        )

    return transact(
        allow_nested=allow_nested,
        check_nesting=check_nesting,
        commit=commit,
        context_var=_CONTEXT_VAR,
        create_context=create_context,
        rollback=rollback,
        session_id=session_id,
        start=start,
    )
