from _typeshed import Incomplete
from collections.abc import Sequence
from radkit_client.async_.exceptions import ClientError

__all__ = ['ExecError', 'ExecPendingError', 'ExecMapError']

class ExecError(ClientError):
    errors: Incomplete
    def __init__(self, errors: str | Sequence[str]) -> None: ...

class ExecPendingError(ExecError):
    def __init__(self) -> None: ...

class ExecMapError(ExecError):
    inner_exception: Incomplete
    __cause__: Incomplete
    def __init__(self, inner_exception: BaseException) -> None: ...
