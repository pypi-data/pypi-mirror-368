from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar

from .._session_id import SessionId
from ._transaction_context import TransactionContextT
from .transaction_id import TransactionId


def get_transaction_id(
    context_var: ContextVar[Mapping[SessionId, TransactionContextT]],
    session_id: SessionId,
    /,
) -> TransactionId | None:
    global_context = context_var.get()
    session_context = global_context.get(session_id)
    return None if session_context is None else session_context.transaction_id
