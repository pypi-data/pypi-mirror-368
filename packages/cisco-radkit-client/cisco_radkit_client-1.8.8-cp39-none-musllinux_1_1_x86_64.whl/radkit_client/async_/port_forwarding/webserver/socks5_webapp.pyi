from ...client import AsyncClient
from _typeshed import Incomplete
from pydantic import BaseModel
from radkit_common.identities import ServiceID

__all__ = ['Socks5WebApp']

class Socks5WebApp:
    app: Incomplete
    def __init__(self, client: AsyncClient) -> None: ...

class _Device(BaseModel):
    name: str
    deviceType: str
    description: str
    forwardedTcpPorts: str
    supportsHttp: bool

class _DeviceTypeEntry(BaseModel):
    name: str
    display: str
    httpRequireDummyCredentials: bool

class _Service(BaseModel):
    name: str
    serviceId: ServiceID | None
    domain: str | None
    inventory: list[_Device]
    deviceTypes: list[_DeviceTypeEntry] | None

class _ClientState(BaseModel):
    connectedDomains: list[_ConnectedDomain]

class _ConnectedDomain(BaseModel):
    identity: str | None
    name: str | None

class _State(BaseModel):
    services: list[_Service]
    client: _ClientState
