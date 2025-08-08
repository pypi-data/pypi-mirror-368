from .from_async import Portal, SyncWrapper
from _typeshed import Incomplete
from radkit_common.access.client.auth_flows import AsyncAuthFlow, AuthFlowType
from radkit_common.identities import EndpointID

__all__ = ['wrap_auth_flow', 'wrap_auth_flow_or_none', 'AuthFlow', 'AccessTokenAuthFlow', 'BasicAuthFlow', 'CertificateAuthFlow', 'OIDCAuthFlow']

def wrap_auth_flow(auth_flow: AsyncAuthFlow, portal: Portal) -> AuthFlow: ...
def wrap_auth_flow_or_none(value: AsyncAuthFlow | None, portal: Portal) -> AuthFlow | None: ...

class AuthFlow(SyncWrapper[AsyncAuthFlow]):
    @property
    def type(self) -> AuthFlowType: ...
    @property
    def identity(self) -> EndpointID: ...
    @property
    def admin_level(self) -> int: ...
    @property
    def is_ready(self) -> bool: ...
    @property
    def token(self) -> str | None: ...

class AccessTokenAuthFlow(AuthFlow):
    reauthenticate: Incomplete

class BasicAuthFlow(AuthFlow):
    reauthenticate: Incomplete

class CertificateAuthFlow(AuthFlow):
    reauthenticate: Incomplete
    certificate_renewed: Incomplete
    certificate_renewed_at: Incomplete
    new_certificate_path: Incomplete
    clear_certificate_renewal: Incomplete

class OIDCAuthFlow(AuthFlow):
    reauthenticate: Incomplete
    oauth_provider: Incomplete
