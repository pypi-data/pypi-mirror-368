from .bdb import AsyncBDB
from .csone import AsyncCSOne
from .cxd import AsyncCXD
from dataclasses import dataclass
from radkit_client.async_.state import AsyncClientState

__all__ = ['AsyncIntegrations']

@dataclass
class AsyncIntegrations:
    def __init__(self, client_state: AsyncClientState) -> None: ...
    def cxd(self) -> AsyncCXD: ...
    def csone(self) -> AsyncCSOne: ...
    def bdb(self) -> AsyncBDB: ...
