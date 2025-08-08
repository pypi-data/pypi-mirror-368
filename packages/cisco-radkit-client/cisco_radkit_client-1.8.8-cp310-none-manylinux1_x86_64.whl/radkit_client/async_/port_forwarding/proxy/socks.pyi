from ..connections import Connection
from .base import ProxyGetHandlerForAddressPort, ProxyValidateLoginHandler
from anyio.abc import SocketStream
from dataclasses import dataclass

__all__ = ['SocksProxy']

@dataclass
class SocksProxy:
    socket_stream: SocketStream
    connection: Connection
    get_handler_for_address_port: ProxyGetHandlerForAddressPort
    validate_login: ProxyValidateLoginHandler
    def __post_init__(self) -> None: ...
    async def run(self) -> None: ...
