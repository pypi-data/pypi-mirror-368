from ..cloud_connections import CloudConnection
from ..from_async import SyncDictWrapper
from _typeshed import Incomplete
from radkit_client.async_.integrations.cxd import AnyAsyncCXDTarget, AsyncCXD, AsyncCXDClientCredentialsAuthenticator, AsyncCXDRADKitCloudClientAuthenticator, AsyncCXDTarget, AsyncCXDTargetsDict, AsyncCXDTokenAuthenticator, AsyncOfflineCXDTarget, CXDError as CXDError
from radkit_client.sync.from_async.sync_wrapper import SyncWrapper
from typing import NoReturn

__all__ = ['CXD', 'CXDError', 'CXDClientCredentialsAuthenticator', 'CXDTokenAuthenticator', 'CXDRADKitCloudClientAuthenticator', 'AnyCXDAuthenticator', 'CXDTarget', 'OfflineCXDTarget', 'CXDTargetsDict', 'AnyCXDTarget']

class CXDTarget(SyncWrapper[AsyncCXDTarget]):
    target: Incomplete
    authenticator: Incomplete

class OfflineCXDTarget(SyncWrapper[AsyncOfflineCXDTarget]):
    target: Incomplete
    token: Incomplete
    hostname: Incomplete
AnyCXDTarget = CXDTarget | OfflineCXDTarget

class CXDTargetsDict(SyncDictWrapper[AsyncCXDTargetsDict, str, AnyAsyncCXDTarget, AnyCXDTarget]): ...

class CXDClientCredentialsAuthenticator(SyncWrapper[AsyncCXDClientCredentialsAuthenticator]):
    client_id: Incomplete
    client_secret: Incomplete
    user_email: Incomplete

class CXDTokenAuthenticator(SyncWrapper[AsyncCXDTokenAuthenticator]):
    token: Incomplete

class CXDRADKitCloudClientAuthenticator(SyncWrapper[AsyncCXDRADKitCloudClientAuthenticator]):
    domain: Incomplete
    connection: Incomplete
    client_id: Incomplete
    oauth_provider: Incomplete
AnyCXDAuthenticator = CXDClientCredentialsAuthenticator | CXDRADKitCloudClientAuthenticator | CXDTokenAuthenticator

class CXD(SyncWrapper[AsyncCXD]):
    def set_default_authenticator_from_cloud_connection(self, connection: CloudConnection) -> None: ...
    set_default_authenticator_from_oauth_token: Incomplete
    set_default_authenticator_from_client_id_secret: Incomplete
    default_authenticator: Incomplete
    add_target_from_upload_token: Incomplete
    add_target_from_client_id_secret: Incomplete
    add_target_from_oauth_token: Incomplete
    add_target_from_default_authenticator: Incomplete
    def add_target_from_cloud_connection(self, target: str, connection: CloudConnection | None = None, set_default: bool = False) -> None: ...
    targets: Incomplete
    remove_target: Incomplete
    set_default_target: Incomplete
    default_target: Incomplete
    get_upload_parameters: Incomplete
    upload_to_cxd: Incomplete
    __call__ = get_upload_parameters
    def authenticate(self, *_: object, **__: object) -> NoReturn: ...
    def add_target(self, *_: object, **__: object) -> NoReturn: ...
