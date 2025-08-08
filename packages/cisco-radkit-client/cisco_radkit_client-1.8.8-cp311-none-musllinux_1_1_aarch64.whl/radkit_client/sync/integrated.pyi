from .from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.integrated import AsyncIntegratedService, AsyncIntegratedServiceCloudRpc, AsyncIntegratedServiceDirectRpc, AsyncIntegratedServiceSecrets, AsyncIntegratedServiceSessionLogs, AsyncIntegratedServiceUiWebserver
from radkit_service.control_api import ControlAPI

__all__ = ['IntegratedService', 'IntegratedServiceUiWebserver', 'IntegratedServiceDirectRpc', 'IntegratedServiceCloudRpc', 'IntegratedServiceSessionLogs', 'IntegratedServiceSecrets']

class IntegratedServiceUiWebserver(SyncWrapper[AsyncIntegratedServiceUiWebserver]):
    enable: Incomplete
    disable: Incomplete
    is_enabled: Incomplete
    address: Incomplete
    sha256_fingerprint: Incomplete

class IntegratedServiceDirectRpc(SyncWrapper[AsyncIntegratedServiceDirectRpc]):
    enable: Incomplete
    disable: Incomplete
    is_enabled: Incomplete
    sha256_fingerprint: Incomplete
    endpoints: Incomplete

class IntegratedServiceCloudRpc(SyncWrapper[AsyncIntegratedServiceCloudRpc]):
    enable: Incomplete
    disable: Incomplete
    is_enabled: Incomplete
    domain: Incomplete
    is_enrolled: Incomplete
    enroll: Incomplete
    service_id: Incomplete
    status: Incomplete

class IntegratedServiceSessionLogs(SyncWrapper[AsyncIntegratedServiceSessionLogs]):
    directory: Incomplete
    max_age_in_days: Incomplete

class IntegratedServiceSecrets(SyncWrapper[AsyncIntegratedServiceSecrets]):
    path: Incomplete

class IntegratedService(SyncWrapper[AsyncIntegratedService]):
    service: Incomplete
    e2ee_sha256_fingerprint: Incomplete
    ui_webserver: Incomplete
    direct_rpc: Incomplete
    cloud_rpc: Incomplete
    session_logs: Incomplete
    secrets: Incomplete
    panel: Incomplete
    suppress_logs: Incomplete
    unsuppress_logs: Incomplete
    terminate: Incomplete
    @property
    def control_api(self) -> ControlAPI: ...
