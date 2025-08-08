from .from_async import Portal, SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.model import HttpVerb as HttpVerb, SwaggerAPIStatus as SwaggerAPIStatus
from radkit_client.async_.swagger import AsyncSwaggerAPI, AsyncSwaggerPath, AsyncSwaggerPathOperation, AsyncSwaggerPathOperationsDict, AsyncSwaggerPathsDict, AsyncSwaggerResponse
from radkit_common.identities import ServiceID
from typing_extensions import Self

__all__ = ['HttpVerb', 'SwaggerAPI', 'SwaggerPathsDict', 'SwaggerPath', 'SwaggerPathOperationsDict', 'SwaggerPathOperation', 'SwaggerResponse', 'SwaggerAPIStatus']

class SwaggerResponse(SyncWrapper[AsyncSwaggerResponse]):
    endpoint: Incomplete
    method: Incomplete
    device: Incomplete
    device_name: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    status_code: Incomplete
    status_phrase: Incomplete
    status_text: Incomplete
    response_code: Incomplete
    url: Incomplete
    content_type: Incomplete
    content: Incomplete
    text: Incomplete
    json: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def serial(self) -> ServiceID | None: ...

class SwaggerPathOperation(SyncWrapper[AsyncSwaggerPathOperation]):
    description: Incomplete
    parameters: Incomplete
    call: Incomplete

class SwaggerPathOperationsDict(SyncDictWrapper[AsyncSwaggerPathOperationsDict, HttpVerb, AsyncSwaggerPathOperation, SwaggerPathOperation]): ...

class SwaggerPath(SyncWrapper[AsyncSwaggerPath]):
    path: Incomplete
    operations: Incomplete
    request: Incomplete
    get: Incomplete
    post: Incomplete
    patch: Incomplete
    put: Incomplete
    delete: Incomplete
    def __init__(self, _async_object: AsyncSwaggerPath, _portal: Portal) -> None: ...

class SwaggerPathsDict(SyncDictWrapper[AsyncSwaggerPathsDict, str, AsyncSwaggerPath, SwaggerPath]): ...

class SwaggerAPI(SyncWrapper[AsyncSwaggerAPI]):
    status: Incomplete
    metadata: Incomplete
    paths: Incomplete
    call_path: Incomplete
    get: Incomplete
    post: Incomplete
    patch: Incomplete
    put: Incomplete
    delete: Incomplete
