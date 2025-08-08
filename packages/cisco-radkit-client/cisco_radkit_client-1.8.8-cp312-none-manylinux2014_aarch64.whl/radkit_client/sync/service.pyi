from .from_async import SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.model.service import ServiceLoadingStatus as ServiceLoadingStatus
from radkit_client.async_.service import AsyncService, AsyncServiceCapabilities, AsyncServiceParameters, ServiceCapability, ServiceStatus as ServiceStatus
from radkit_common.identities import ServiceID
from typing_extensions import Self

__all__ = ['ServiceParameters', 'ServiceCapabilities', 'Service', 'ServiceStatus', 'ServiceLoadingStatus']

class ServiceParameters(SyncWrapper[AsyncServiceParameters]):
    name: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    service: Incomplete
    @property
    def serial(self) -> ServiceID | None: ...

class ServiceCapabilities(SyncDictWrapper[AsyncServiceCapabilities, int, ServiceCapability, ServiceCapability]):
    service_id: Incomplete
    service_version: Incomplete
    status: Incomplete
    service: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def serial(self) -> ServiceID | None: ...

class Service(SyncWrapper[AsyncService]):
    reload: Incomplete
    status: Incomplete
    connection: Incomplete
    domain: Incomplete
    domain_name: Incomplete
    target: Incomplete
    name: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    loading_error: Incomplete
    inventory: Incomplete
    logout: Incomplete
    version: Incomplete
    capabilities: Incomplete
    e2ee_supported: Incomplete
    e2ee_active: Incomplete
    set_e2ee_credentials: Incomplete
    set_e2ee_fingerprint: Incomplete
    supported_compression_methods: Incomplete
    direct_rpc_url: Incomplete
    params: Incomplete
    requests: Incomplete
    session_logs: Incomplete
    sessions: Incomplete
    port_forwards: Incomplete
    client: Incomplete
    ping: Incomplete
    get_e2ee_information: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    update_inventory: Incomplete
    update_capabilities: Incomplete
    @property
    def serial(self) -> ServiceID | None: ...
