import socket as _socket
from ..device import AsyncDevice
from ..formatting.smart_repr import SmartPtRepr
from ..state import AsyncServiceState
from .streams import StreamRequestReader, StreamRequestWriter
from .utils import ExplanatoryLock
from enum import Enum
from uuid import UUID

__all__ = ['AsyncSocketForwarder', 'SocketForwarderStatus']

class SocketForwarderStatus(Enum):
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    STOPPED = 'STOPPED'

class AsyncSocketForwarder:
    __pt_repr__: SmartPtRepr[AsyncSocketForwarder]
    def __init__(self, service_state: AsyncServiceState, device_uuid: UUID, streams_lock: ExplanatoryLock, reader: StreamRequestReader, writer: StreamRequestWriter, buffer_size: int = 4096) -> None: ...
    def status(self) -> SocketForwarderStatus: ...
    def device_name(self) -> str: ...
    def device(self) -> AsyncDevice: ...
    def socket(self) -> _socket.socket: ...
    async def start(self) -> _socket.socket: ...
    async def stop(self) -> None: ...
