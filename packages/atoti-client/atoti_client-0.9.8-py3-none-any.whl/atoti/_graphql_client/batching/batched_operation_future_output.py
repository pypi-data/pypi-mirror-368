from collections.abc import Callable, Mapping
from typing import (
    Concatenate,
    Final,
    Generic,
    ParamSpec,
    TypeVar,
    final,
)

_OperationOutput = TypeVar("_OperationOutput")

_P = ParamSpec("_P")


@final
class BatchedOperationFutureOutput(Generic[_OperationOutput]):
    def __init__(self, *, flush_batch_prematurely: Callable[[], None]) -> None:
        self._flush_batch_prematurely: Final = flush_batch_prematurely
        self._output: _OperationOutput | None = None
        self._validate_output: (
            tuple[
                Callable[..., None],
                tuple[object, ...],
                Mapping[str, object],
            ]
            | None
        ) = None

    def _set_output(self, output: _OperationOutput, /) -> None:
        assert self._output is None, "Output has already been set."
        self._output = output
        if self._validate_output is not None:
            callback, args, kwargs = self._validate_output
            callback(output, *args, **kwargs)

    def set_output_validator(
        self,
        callback: Callable[Concatenate[_OperationOutput, _P], None],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> None:
        """Set the callback that will be called to validate the output of this operation once the batched operations are executed."""
        assert self._output is None, "Output has already been set."
        assert self._validate_output is None, "Validator has already been set."
        self._validate_output = callback, args, kwargs

    def flush_batch_prematurely(self) -> _OperationOutput:
        """Flush the batched operations and return the output of this operation.

        Warning:
            This should be avoided as explained in `OperationBatcher.flush_prematurely`.

        """
        assert self._validate_output is None, (
            "Cannot request output after setting validator."
        )
        self._flush_batch_prematurely()
        assert self._output is not None, "Output should have been set."
        return self._output
