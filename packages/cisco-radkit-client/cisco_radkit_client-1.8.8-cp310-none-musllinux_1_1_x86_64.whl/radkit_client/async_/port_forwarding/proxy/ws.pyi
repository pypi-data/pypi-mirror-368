from ..base import AnySocketStream
from .base import HttpStartResponse, WebSocketRequestHandler
from dataclasses import dataclass
from typing import Protocol

__all__ = ['WebSocketForwarder', 'GetSocketStreamAndTrailingData']

class GetSocketStreamAndTrailingData(Protocol):
    async def __call__(self, start_response: HttpStartResponse) -> tuple[AnySocketStream, bytes]: ...

@dataclass
class WebSocketForwarder:
    authority: str
    target: str
    request_headers: list[tuple[str, str]]
    get_socket_stream_and_trailing_data: GetSocketStreamAndTrailingData
    websocket_request_handler: WebSocketRequestHandler
    async def run(self) -> None: ...
