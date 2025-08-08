from collections.abc import Iterable
from enum import Enum

__all__ = ['ExecStatus']

class ExecStatus(Enum):
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'
    PARTIAL_SUCCESS = 'PARTIAL_SUCCESS'
    @classmethod
    def from_multiple(cls, statuses: Iterable[ExecStatus]) -> ExecStatus: ...
    def __eq__(self, other: object) -> bool: ...
