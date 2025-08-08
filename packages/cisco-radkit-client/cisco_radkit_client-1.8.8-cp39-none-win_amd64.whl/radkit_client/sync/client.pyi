from .admin_client import AdminClient
from .auth_flows import AuthFlow
from .cloud_connections import CloudConnection
from .from_async import SyncDictWrapper, SyncWrapper
from .integrated import IntegratedService
from .service import Service
from _typeshed import Incomplete
from collections.abc import Callable, Coroutine, Generator
from contextlib import AbstractAsyncContextManager, contextmanager
from radkit_client.async_.client import AsyncClient, AsyncForwardersDict, AsyncServicesDict, ClientStatus as ClientStatus, ForwarderInfo
from radkit_client.async_.model import ClientEnrollInfo, ServiceEnrollInfo
from radkit_client.async_.service import AsyncService
from radkit_common.access.client.auth_flows import AuthFlowType
from radkit_common.access.oauth import OAuthConnectResponse
from radkit_common.access.results import ErrorResult
from radkit_common.domains import Domain
from radkit_common.identities import ClientID, Email, ServiceID
from radkit_common.types import CustomSecretStr, OAuthProvider
from radkit_service.backends.devices_backend import DevicesBackend
from typing import Any, NoReturn
from typing_extensions import Self

__all__ = ['Client', 'ClientStatus', 'ForwardersDict', 'ServicesDict']

class ServicesDict(SyncDictWrapper[AsyncServicesDict, int, AsyncService, Service]):
    client: Incomplete

class ForwardersDict(SyncDictWrapper[AsyncForwardersDict, int, ForwarderInfo, ForwarderInfo]):
    client: Incomplete

class Client(SyncWrapper[AsyncClient]):
    forwarders: Incomplete
    socks_proxy: Incomplete
    http_proxy: Incomplete
    status: Incomplete
    cloud_connections: Incomplete
    services: Incomplete
    requests: Incomplete
    session_logs: Incomplete
    sessions: Incomplete
    port_forwards: Incomplete
    set_default_domain: Incomplete
    get_default_domain: Incomplete
    start_http_proxy: Incomplete
    stop_http_proxy: Incomplete
    start_socks_proxy: Incomplete
    stop_socks_proxy: Incomplete
    start_ssh_proxy: Incomplete
    stop_ssh_proxy: Incomplete
    sso_login: Incomplete
    cloud_connection_from_sso_login: Incomplete
    basic_login: Incomplete
    access_token_login: Incomplete
    certificate_login: Incomplete
    logout: Incomplete
    oauth_connect_only: Incomplete
    get_oauth_provider_info: Incomplete
    service_from_rpc_target: Incomplete
    service_direct: Incomplete
    enroll_client_from_otp: Incomplete
    read_identity_certificate: Incomplete
    write_identity_certificate: Incomplete
    integrations: Incomplete
    support_package: Incomplete
    @classmethod
    @contextmanager
    def create(cls, default_domain: Domain | None | str = None) -> Generator[Self, None, None]: ...
    def service(self, service_id: ServiceID | str, *, connection: CloudConnection | None = None, e2ee_fingerprint: str | None = None, access_token: str | None = None, name: str | None = None) -> Service: ...
    def service_cloud(self, service_id: ServiceID, *, connection: CloudConnection | None = None, e2ee_fingerprint: str | None = None, access_token: str | None = None, name: str | None = None) -> Service: ...
    def service_direct_with_sso(self, service_id: ServiceID, *, connection: CloudConnection | None = None, e2ee_fingerprint: str | None = None, host: str = 'localhost', port: int = 8181, name: str | None = None) -> Service: ...
    def service_integrated(self, *_: object, **__: object) -> None: ...
    def create_service(self, *, suppress_logs: bool = False, headless: bool = False, superadmin_password: CustomSecretStr | str | None = None, create_extra_devices_backend: Callable[[], AbstractAsyncContextManager[DevicesBackend]] | None = None) -> IntegratedService: ...
    def grant_client_otp(self, client_id: ClientID | None = None, client_owner_email: Email | None = None, connection: CloudConnection | None = None, description: str = '') -> ClientEnrollInfo | ErrorResult: ...
    def grant_service_otp(self, service_id: ServiceID | None = None, service_owner_email: Email | None = None, connection: CloudConnection | None = None, description: str = '') -> ServiceEnrollInfo | None: ...
    def enroll_client(self, client_id: ClientID | None = None, private_key_password: str | None = None, overwrite_certificate: bool | None = None, connection: CloudConnection | None = None, description: str = '') -> None: ...
    def reauthenticate(self, access_token: str | None = None, basic_auth_password: str | None = None, oauth_connect_response: OAuthConnectResponse | None = None, connection: CloudConnection | None = None) -> None: ...
    def admin_client(self, connection: CloudConnection | None = None) -> AdminClient: ...
    def start_background_job(self, func: Callable[[], Coroutine[Any, Any, None]]) -> None: ...
    @property
    def authenticator(self) -> AuthFlow | None: ...
    @property
    def forwarder_connection_status(self) -> ForwardersDict: ...
    @property
    def identity(self) -> ClientID: ...
    @property
    def client_id(self) -> ClientID: ...
    @property
    def access_token(self) -> str | None: ...
    @property
    def authentication_method(self) -> AuthFlowType | None: ...
    @property
    def oauth_provider(self) -> str | OAuthProvider | None: ...
    @property
    def authenticators(self) -> NoReturn: ...
    @property
    def oauth_providers(self) -> NoReturn: ...
    @property
    def access_tokens(self) -> NoReturn: ...
