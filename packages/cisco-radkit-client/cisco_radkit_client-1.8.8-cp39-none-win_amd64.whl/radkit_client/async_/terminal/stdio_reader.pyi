from _typeshed import Incomplete
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

__all__ = ['StdioReader', 'STYLE']

class StdioReader:
    def __init__(self, help_text: str) -> None: ...
    @asynccontextmanager
    async def read_input(self) -> AsyncGenerator[AsyncGenerator[bytes, None], None]: ...

STYLE: Incomplete
