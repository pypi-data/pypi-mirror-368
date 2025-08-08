from .from_async import SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.cloud_connections import AsyncCloudConnection, AsyncCloudConnectionsDict, CloudConnectionError as CloudConnectionError

__all__ = ['CloudConnection', 'CloudConnectionsDict', 'unwrap_cloud_connection_or_none', 'CloudConnectionError']

class CloudConnection(SyncWrapper[AsyncCloudConnection]):
    is_default: Incomplete
    domain: Incomplete
    client_id: Incomplete
    type: Incomplete
    admin_level: Incomplete
    oauth_provider: Incomplete
    access_token: Incomplete
    is_ready: Incomplete
    client: Incomplete
    auth_flow: Incomplete
    logout: Incomplete
    reauthenticate: Incomplete

class CloudConnectionsDict(SyncDictWrapper[AsyncCloudConnectionsDict, int, AsyncCloudConnection, CloudConnection]):
    client: Incomplete
    default: Incomplete
    filter: Incomplete
    first: Incomplete

def unwrap_cloud_connection_or_none(connection: CloudConnection | None) -> AsyncCloudConnection | None: ...
