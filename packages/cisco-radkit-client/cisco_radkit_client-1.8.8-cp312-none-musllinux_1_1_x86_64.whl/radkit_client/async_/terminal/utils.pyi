import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

__all__ = ['ExplanatoryLock']

@dataclass
class ExplanatoryLock:
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    @asynccontextmanager
    async def lock_or_fail(self, message: str = '') -> AsyncGenerator[None, None]: ...
