from ..base import AnySocketStream
from _typeshed import Incomplete
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from dataclasses import dataclass
from typing import Protocol

__all__ = ['HttpRequest', 'HttpStartResponse', 'HttpRequestHandler', 'HttpWebSocketRequest', 'WebSocketFrame', 'WebSocketRequestHandler', 'SocketStreamHandler', 'ProxyGetHandlerForAddressPort', 'ProxyValidateLoginHandler', 'remove_http_response_headers', 'PROXY_AUTHENTICATE_HEADER', 'INDEX_AUTHENTICATE_HEADER']

@dataclass
class HttpRequest:
    method: str
    authority: str
    target: str
    request_headers: list[tuple[str, str]]

@dataclass
class HttpStartResponse:
    status_code: int
    response_headers: list[tuple[str, str]]

class HttpRequestHandler(Protocol):
    async def __call__(self, http_request: HttpRequest, upload_receive_stream: MemoryObjectReceiveStream[bytes], download_send_stream: MemoryObjectSendStream[HttpStartResponse | bytes]) -> None: ...

@dataclass
class HttpWebSocketRequest:
    authority: str
    target: str
    request_headers: list[tuple[str, str]]

@dataclass
class WebSocketFrame:
    data: bytes | str
    message_finished: bool

class WebSocketRequestHandler(Protocol):
    async def __call__(self, websocket_request: HttpWebSocketRequest, upload_receive_stream: MemoryObjectReceiveStream[WebSocketFrame], download_send_stream: MemoryObjectSendStream[HttpStartResponse | WebSocketFrame]) -> None: ...

class SocketStreamHandler(Protocol):
    async def __call__(self, socket_stream: AnySocketStream) -> None: ...

class ProxyGetHandlerForAddressPort(Protocol):
    async def __call__(self, address: str, port: int) -> SocketStreamHandler | None: ...

class ProxyValidateLoginHandler(Protocol):
    def __call__(self, username: str, password: str) -> bool: ...

PROXY_AUTHENTICATE_HEADER: Incomplete
INDEX_AUTHENTICATE_HEADER: Incomplete

def remove_http_response_headers(headers: list[tuple[str, str]]) -> list[tuple[str, str]]: ...
