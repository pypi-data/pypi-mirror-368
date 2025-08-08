from ...state import AsyncClientState
from ..base import AsyncPortForwarder
from ..connections import AsyncEndpointConnectionsDict
from _typeshed import Incomplete
from collections.abc import Callable
from enum import Enum
from typing import Any

__all__ = ['ProxyProtocol', 'AsyncProxyPortForwarder']

class ProxyProtocol(Enum):
    HTTP = 'HTTP'
    SOCKS_V5 = 'SOCKS_V5'

class AsyncProxyPortForwarder(AsyncPortForwarder):
    __pt_repr__: Incomplete
    def __init__(self, client_state: AsyncClientState, local_port: int, local_address: str, username: str | None = None, password: str | None = None, protocol: ProxyProtocol = ..., max_connections: int | None = 50, server_startup_timeout: float = 2.0) -> None: ...
    def protocol(self) -> ProxyProtocol: ...
    def endpoints_connections(self) -> AsyncEndpointConnectionsDict: ...
    async def start(self) -> None: ...
    def add_procedure(self, name: str, handler: Callable[..., Any]) -> None: ...
