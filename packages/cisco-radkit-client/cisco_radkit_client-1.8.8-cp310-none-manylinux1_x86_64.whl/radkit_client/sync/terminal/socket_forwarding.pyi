from ..from_async import SyncWrapper
from _typeshed import Incomplete
from pexpect.socket_pexpect import SocketSpawn
from radkit_client.async_.terminal.socket_forwarding import AsyncSocketForwarder, SocketForwarderStatus as SocketForwarderStatus
from typing import Any, AnyStr
from typing_extensions import Self

__all__ = ['SocketForwarder', 'SocketForwarderStatus']

class SocketForwarder(SyncWrapper[AsyncSocketForwarder]):
    status: Incomplete
    device_name: Incomplete
    device: Incomplete
    socket: Incomplete
    start: Incomplete
    stop: Incomplete
    def spawn_pexpect(self, args: Any = None, timeout: int = 30, maxread: int = 2000, searchwindowsize: Any = None, logfile: Any = None, encoding: Any = None, codec_errors: str = 'strict', use_poll: bool = False) -> SocketSpawn[AnyStr]: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *_: object) -> None: ...
