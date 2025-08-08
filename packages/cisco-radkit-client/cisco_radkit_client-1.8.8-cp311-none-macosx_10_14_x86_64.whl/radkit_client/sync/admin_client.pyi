from .auth_flows import AuthFlow
from .from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.admin_client import AsyncAdminClient, AsyncAdminClientParameters

__all__ = ['AdminClientParameters', 'AdminClient']

class AdminClientParameters(SyncWrapper[AsyncAdminClientParameters]):
    client_id: Incomplete
    domain: Incomplete
    client: Incomplete
    auth_flow: Incomplete

class AdminClient(SyncWrapper[AsyncAdminClient]):
    params: Incomplete
    client_id: Incomplete
    admin_level: Incomplete
    domain: Incomplete
    domain_name: Incomplete
    connection: Incomplete
    authentication_method: Incomplete
    status: Incomplete
    access_token: Incomplete
    grant_service_otp: Incomplete
    grant_client_otp: Incomplete
    enroll_client: Incomplete
    create_user: Incomplete
    get_user: Incomplete
    get_user_endpoints: Incomplete
    get_endpoints: Incomplete
    get_user_data: Incomplete
    update_user: Incomplete
    delete_user: Incomplete
    get_certificate: Incomplete
    revoke_certificate: Incomplete
    get_resource_limit: Incomplete
    reset_resource_limit: Incomplete
    get_auditor_counters: Incomplete
    get_service_state: Incomplete
    generate_api_token: Incomplete
    revoke_api_tokens: Incomplete
    list_api_tokens: Incomplete
    generate_client_credentials: Incomplete
    revoke_client_credentials: Incomplete
    list_client_credentials: Incomplete
    @property
    def authenticator(self) -> AuthFlow: ...
