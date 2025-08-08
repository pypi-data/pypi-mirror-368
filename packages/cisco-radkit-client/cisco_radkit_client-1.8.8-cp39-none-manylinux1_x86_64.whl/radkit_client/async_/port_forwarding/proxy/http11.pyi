from ..base import AnySocketStream
from .base import HttpRequestHandler, ProxyGetHandlerForAddressPort, ProxyValidateLoginHandler, WebSocketRequestHandler
from dataclasses import dataclass

__all__ = ['Http11Forwarder']

@dataclass
class Http11Forwarder:
    socket_stream: AnySocketStream
    request_handler: HttpRequestHandler
    websocket_request_handler: WebSocketRequestHandler | None
    get_handler_for_address_port: ProxyGetHandlerForAddressPort | None = ...
    validate_login: ProxyValidateLoginHandler | None = ...
    def __post_init__(self) -> None: ...
    async def run(self) -> None: ...
