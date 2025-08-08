from _typeshed import Incomplete
from contextlib import AbstractContextManager
from typing_extensions import Self

__all__ = ['StdioWriter']

class StdioWriter:
    decoder: Incomplete
    def __init__(self) -> None: ...
    @classmethod
    def create(cls) -> AbstractContextManager[Self]: ...
    def write_and_flush(self, data: bytes) -> None: ...
