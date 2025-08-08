from ..auto_incrementing_id import Id
from ..device import AsyncDevice
from ..state import AsyncServiceState
from .base import AsyncPortForwarder
from .connections import AsyncConnections
from _typeshed import Incomplete
from uuid import UUID

__all__ = ['AsyncTCPPortForwarder']

class AsyncTCPPortForwarder(AsyncPortForwarder):
    __pt_repr__: Incomplete
    id: Id
    def __init__(self, service_state: AsyncServiceState, device_uuid: UUID, local_port: int, local_address: str, destination_port: int, server_startup_timeout: float = 2.0) -> None: ...
    def connections(self) -> AsyncConnections: ...
    def device(self) -> AsyncDevice: ...
    def device_name(self) -> str: ...
    def destination_port(self) -> int: ...
