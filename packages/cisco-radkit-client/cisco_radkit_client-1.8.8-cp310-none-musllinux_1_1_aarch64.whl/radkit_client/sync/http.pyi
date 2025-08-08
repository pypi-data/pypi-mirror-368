from .from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.http import AsyncEraseAuthenticationTokensResult, AsyncHttpApi, AsyncHttpOverlayHeadersDict, AsyncHttpResponse, HttpApiError as HttpApiError
from radkit_client.sync.from_async.sync_wrapper import SyncDictWrapper
from radkit_common.identities import ServiceID
from typing_extensions import Self

__all__ = ['HttpApi', 'HttpApiError', 'HttpResponse', 'HttpOverlayHeadersDict']

class HttpResponse(SyncWrapper[AsyncHttpResponse]):
    device: Incomplete
    device_name: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    status: Incomplete
    @property
    def request(self) -> _AnyHttpRequest: ...
    url: Incomplete
    endpoint: Incomplete
    method: Incomplete
    status_code: Incomplete
    status_phrase: Incomplete
    status_text: Incomplete
    headers: Incomplete
    cookies: Incomplete
    content: Incomplete
    content_type: Incomplete
    text: Incomplete
    json: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def result(self) -> Self: ...
    @property
    def serial(self) -> ServiceID | None: ...

class EraseAuthenticationTokensResult(SyncWrapper[AsyncEraseAuthenticationTokensResult]):
    device_name: Incomplete
    device: Incomplete
    status: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    done: Incomplete
    success: Incomplete
    failure: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...

class HttpOverlayHeadersDict(SyncDictWrapper[AsyncHttpOverlayHeadersDict, str, str, str]):
    __setitem__: Incomplete
    __delitem__: Incomplete

class HttpApi(SyncWrapper[AsyncHttpApi]):
    get: Incomplete
    options: Incomplete
    head: Incomplete
    post: Incomplete
    patch: Incomplete
    put: Incomplete
    delete: Incomplete
    erase_auth_tokens: Incomplete
    overlay_headers: Incomplete
HTTP_API = HttpApi
HTTP_APIError = HttpApiError
