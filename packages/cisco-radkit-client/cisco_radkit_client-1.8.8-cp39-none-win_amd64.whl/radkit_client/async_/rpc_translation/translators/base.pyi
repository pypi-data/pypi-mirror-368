from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from radkit_common.rpc import RPC_Definition, RequestError
from radkit_common.rpc.client import FailUpload
from typing import Any, Generic

__all__ = ['OutgoingRequestTranslator']

@dataclass
class OutgoingRequestTranslator(Generic[_FromRequestModel, _FromResponseModel, _FromUploadModel, _ToRequestModel, _ToResponseModel, _ToUploadModel]):
    from_rpc_definition: RPC_Definition[_FromRequestModel, _FromResponseModel, _FromUploadModel]
    to_rpc_definition: RPC_Definition[_ToRequestModel, _ToResponseModel, _ToUploadModel]
    handles: Callable[[_FromRequestModel], bool]
    translate_request: Callable[[_FromRequestModel], _ToRequestModel]
    translate_response_stream: Callable[[MemoryObjectReceiveStream[_ToResponseModel | RequestError], MemoryObjectSendStream[_FromResponseModel | RequestError]], Coroutine[Any, Any, Any]]
    translate_upload_stream: Callable[[MemoryObjectReceiveStream[_FromUploadModel | FailUpload], MemoryObjectSendStream[_ToUploadModel | FailUpload]], Coroutine[Any, Any, Any]]
