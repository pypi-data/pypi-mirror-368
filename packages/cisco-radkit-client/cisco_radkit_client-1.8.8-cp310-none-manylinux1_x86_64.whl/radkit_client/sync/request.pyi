from .from_async import SyncWrapper
from _typeshed import Incomplete
from collections.abc import Sequence
from radkit_client.async_.request import AsyncE2EEInformation, AsyncFillerRequest, AsyncSimpleRequest, AsyncStreamRequest, AsyncTransformedFillerRequest, RequestPendingError as RequestPendingError, RequestStatus as RequestStatus
from radkit_client.async_.terminal.streams import AsyncBinaryStreamRequest
from radkit_client.sync.from_async import syncproperty
from typing import Any, Generic
from typing_extensions import Self

__all__ = ['AnySyncRequest', 'SimpleRequest', 'StreamRequest', 'FillerRequest', 'TransformedFillerRequest', 'BinaryStreamRequest', 'RequestStatus', 'E2EEInformation', 'RequestPendingError']

AnySyncRequest: Incomplete

class E2EEInformation(SyncWrapper[AsyncE2EEInformation]):
    request: syncproperty[SyncWrapper[Any], AnySyncRequest]
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    e2ee_used: Incomplete
    domain: Incomplete
    domain_name: Incomplete
    binary_peercert: Incomplete
    sha256_hash: Incomplete
    sha256_hash_hexdigest: Incomplete
    x509_certificate: Incomplete

class SimpleRequest(SyncWrapper[AsyncSimpleRequest[_T_RequestModel, _T_ResponseModel, _T_HandlerResult]], Generic[_T_RequestModel, _T_ResponseModel, _T_HandlerResult]):
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    rpc_name: Incomplete
    event_log: Incomplete
    e2ee_used: Incomplete
    e2ee: Incomplete
    compression_used: Incomplete
    message: Incomplete
    done: Incomplete
    success: Incomplete
    failure: Incomplete
    cancel: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    protocol_results: syncproperty[Any, Sequence[_T_ResponseModel]]
    status: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def result(self) -> Any: ...

class StreamRequest(SyncWrapper[AsyncStreamRequest[_T_RequestModel, _T_ResponseModel, _T_UploadModel]], Generic[_T_RequestModel, _T_ResponseModel, _T_UploadModel]):
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    rpc_name: Incomplete
    event_log: Incomplete
    e2ee_used: Incomplete
    e2ee: Incomplete
    compression_used: Incomplete
    message: Incomplete
    done: Incomplete
    success: Incomplete
    failure: Incomplete
    cancel: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    status: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...

class _FillerRequestMeta(type):
    def __instancecheck__(cls, obj: object) -> bool: ...

class FillerRequest(SyncWrapper[AsyncFillerRequest[_T_RequestModel, _T_ResponseModel, Any]], Generic[_T_RequestModel, _T_ResponseModel, _T_HandlerResult], metaclass=_FillerRequestMeta):
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    rpc_name: Incomplete
    event_log: Incomplete
    e2ee_used: Incomplete
    e2ee: Incomplete
    compression_used: Incomplete
    message: Incomplete
    done: Incomplete
    success: Incomplete
    failure: Incomplete
    cancel: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    status: Incomplete
    total_updates: Incomplete
    failed_updates: Incomplete
    succeeded_updates: Incomplete
    protocol_results: syncproperty[Any, Sequence[_T_ResponseModel]]
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def result(self) -> _T_HandlerResult: ...
    @property
    def full_result(self) -> _T_HandlerResult: ...

class _TransformedFillerRequestMeta(type):
    def __instancecheck__(cls, obj: object) -> bool: ...

class TransformedFillerRequest(SyncWrapper[AsyncTransformedFillerRequest[_T_RequestModel, _T_ResponseModel, Any, Any]], Generic[_T_RequestModel, _T_ResponseModel, _T_HandlerResult, _T_FinalResult], metaclass=_TransformedFillerRequestMeta):
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    rpc_name: Incomplete
    event_log: Incomplete
    e2ee_used: Incomplete
    e2ee: Incomplete
    compression_used: Incomplete
    message: Incomplete
    done: Incomplete
    success: Incomplete
    failure: Incomplete
    cancel: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    status: Incomplete
    total_updates: Incomplete
    failed_updates: Incomplete
    succeeded_updates: Incomplete
    protocol_results: syncproperty[Any, Sequence[_T_ResponseModel]]
    def wait(self, timeout: float | None = None) -> Self: ...
    @property
    def result(self) -> _T_FinalResult: ...
    @property
    def full_result(self) -> _T_HandlerResult: ...
    @property
    def filler_request(self) -> FillerRequest[_T_RequestModel, _T_ResponseModel, _T_HandlerResult]: ...

class BinaryStreamRequest(SyncWrapper[AsyncBinaryStreamRequest[_T_RequestModel, _T_ResponseModel, _T_UploadModel]], Generic[_T_RequestModel, _T_ResponseModel, _T_UploadModel]):
    service_id: Incomplete
    client_id: Incomplete
    client: Incomplete
    service: Incomplete
    rpc_name: Incomplete
    event_log: Incomplete
    e2ee_used: Incomplete
    e2ee: Incomplete
    bytes_read: Incomplete
    bytes_written: Incomplete
    done: Incomplete
    exception: Incomplete
    exception_traceback: Incomplete
    status: Incomplete
