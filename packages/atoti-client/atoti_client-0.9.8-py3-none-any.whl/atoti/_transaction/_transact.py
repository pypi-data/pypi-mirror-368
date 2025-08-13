from __future__ import annotations

from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .._collections import frozendict
from .._session_id import SessionId
from ._transaction_context import TransactionContextT
from .transaction_id import TransactionId


@contextmanager
def transact(
    *,
    allow_nested: bool,
    check_nesting: Callable[[TransactionContextT], None] = lambda _: None,
    commit: Callable[[TransactionId], None],
    context_var: ContextVar[Mapping[SessionId, TransactionContextT]],
    create_context: Callable[[TransactionId], TransactionContextT],
    rollback: Callable[[TransactionId], None],
    session_id: SessionId,
    start: Callable[[], str],
) -> Generator[None, None, None]:
    token: Token[Mapping[SessionId, TransactionContextT]] | None = None

    previous_global_context = context_var.get()
    previous_session_context = previous_global_context.get(session_id)

    if previous_session_context is not None:
        if not allow_nested:
            raise RuntimeError(
                "Cannot start this transaction inside another transaction since nesting is not allowed.",
            )

        check_nesting(previous_session_context)
        yield
        return

    transaction_id = TransactionId(start())
    new_session_context = create_context(transaction_id)
    token = context_var.set(
        frozendict({**previous_global_context, session_id: new_session_context})
    )

    try:
        yield
    except:
        rollback(transaction_id)
        raise
    else:
        commit(transaction_id)
    finally:
        context_var.reset(token)
