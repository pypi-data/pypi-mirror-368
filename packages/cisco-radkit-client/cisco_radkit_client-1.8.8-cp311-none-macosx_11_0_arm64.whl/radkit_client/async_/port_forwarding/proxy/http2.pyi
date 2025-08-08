from ..base import AnySocketStream
from .base import HttpRequestHandler, WebSocketRequestHandler
from dataclasses import dataclass

__all__ = ['Http2Forwarder']

@dataclass
class Http2Forwarder:
    socket_stream: AnySocketStream
    request_handler: HttpRequestHandler
    websocket_request_handler: WebSocketRequestHandler | None
    def __post_init__(self) -> None: ...
    async def run(self) -> None: ...
