from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Final, Generic, Protocol, final

from graphql import DocumentNode, parse as __parse, print_ast

from ._merge_documents import merge_documents
from ._merge_variables import merge_variables
from ._unmerge_output import unmerge_output
from .batched_operation_future_output import (
    BatchedOperationFutureOutput,
    _OperationOutput,
)


class _ExecuteOperation(Protocol):
    def __call__(
        self, single_operation_document: str, /, variables: Mapping[str, object]
    ) -> Mapping[str, Any]: ...


@final
class _BatchedOperation(Generic[_OperationOutput]):
    def __init__(
        self,
        *,
        document: str,
        variables: Mapping[str, object],
        future_output: BatchedOperationFutureOutput[_OperationOutput],
        validate_output: Callable[[Mapping[str, object]], _OperationOutput],
    ) -> None:
        self.document: Final = document
        self.variables: Final = variables
        self.future_output: Final = future_output
        self.validate_output: Final = validate_output


@lru_cache  # The set of documents used by Atoti Python SDK is small and static.
def _parse(document: str, /) -> DocumentNode:
    return __parse(document, no_location=True)


def _execute_batched_operations(
    batched_operations: Sequence[_BatchedOperation[object]],
    /,
    *,
    execute_operation: _ExecuteOperation,
) -> None:
    if not batched_operations:
        return

    document_ast = merge_documents(
        [_parse(operation.document) for operation in batched_operations]
    )
    document = print_ast(document_ast)
    variables = {
        **merge_variables([operation.variables for operation in batched_operations])
    }
    output = execute_operation(document, variables)
    outputs = unmerge_output(output, document_count=len(batched_operations))
    for batched_operation, batched_operation_output_data in zip(
        batched_operations, outputs, strict=True
    ):
        batched_operation_output = batched_operation.validate_output(
            batched_operation_output_data
        )
        batched_operation.future_output._set_output(batched_operation_output)


@final
class OperationBatcher:
    """GraphQL operation batcher.

    Batching improves performance by:

    * reducing latency since what would have been *n* requests to the server become *1*.
    * giving more context to the server allowing it to derive an optimal execution plan (e.g. fewer cube restarts).
    """

    def __init__(
        self,
        *,
        execute_operation: _ExecuteOperation,
    ):
        self._batched_operations: Final[list[_BatchedOperation[object]]] = []
        self._batching: bool = False
        self._execute_operation: Final = execute_operation

    @contextmanager
    def batch(self) -> Generator[None, None, None]:
        """Operations appended inside this context will be batched.

        If a batch is already in progress, the operations appended inside this context will be executed when the outer context exits.
        """
        if self._batching:
            yield
        else:
            self._batching = True
            yield
            try:
                self._flush()
            finally:
                self._batching = False

    @property
    def batch_size(self) -> int:
        return len(self._batched_operations)

    def _flush(self) -> None:
        try:
            _execute_batched_operations(
                self._batched_operations,
                execute_operation=self._execute_operation,
            )
        finally:
            self._batched_operations.clear()

    def submit(
        self,
        *,
        document: str,
        variables: Mapping[str, object],
        validate_output: Callable[[Mapping[str, object]], _OperationOutput],
    ) -> BatchedOperationFutureOutput[_OperationOutput]:
        """Append an operation to the batch, or execute it immediately if batching is disabled.

        All operations in the same batch must share the same operation type.
        """
        future_output = BatchedOperationFutureOutput(  # type: ignore[var-annotated]
            flush_batch_prematurely=self.flush_prematurely
        )
        with self.batch():
            self._batched_operations.append(
                _BatchedOperation(
                    document=document,
                    variables=variables,
                    future_output=future_output,
                    validate_output=validate_output,
                )
            )
        return future_output

    def flush_prematurely(self) -> None:
        """Execute all the operations in the current batch.

        Warning:
            This nullifies the benefits of batching and must only be used by a caller when running the next lines of code requires the batched operations to have been executed by the server.
        """
        self._flush()
