from ..device import AsyncDevice
from ..state import AsyncServiceState
from _typeshed import Incomplete
from collections.abc import Iterator, Mapping
from enum import Enum
from typing import Any, overload
from typing_extensions import Self
from uuid import UUID

__all__ = ['AsyncDeviceToXPathResultsDict', 'AsyncDeviceToSingleXPathResultDict', 'NetconfResultStatus', 'YangDataMapping', 'YangDataSequence', 'AsyncGetXPathsResult', 'AsyncGetSingleXPathResult']

class AsyncDeviceToXPathResultsDict(dict[str, 'AsyncGetXPathsResult']):
    __pt_repr__: Incomplete

class AsyncDeviceToSingleXPathResultDict(dict[str, 'AsyncGetSingleXPathResult']):
    __pt_repr__: Incomplete

class AsyncGetXPathsResult(Mapping[str, 'AsyncGetSingleXPathResult']):
    __pt_repr__: Incomplete
    xpaths: Incomplete
    namespaces: Incomplete
    def __init__(self, service_state: AsyncServiceState, device_uuid: UUID, xpaths: list[str], namespaces: dict[str, dict[str, str]]) -> None: ...
    def device_name(self) -> str: ...
    def device(self) -> AsyncDevice: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __getitem__(self, xpath: str) -> AsyncGetSingleXPathResult: ...
    async def wait(self) -> Self: ...

class NetconfResultStatus(Enum):
    FAILURE = 'FAILURE'
    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'

class AsyncGetSingleXPathResult:
    __pt_repr__: Incomplete
    __to_std_object__: Incomplete
    xpath: Incomplete
    namespaces: Incomplete
    def __init__(self, service_state: AsyncServiceState, device_uuid: UUID, xpath: str, namespaces: dict[str, str]) -> None: ...
    def device_name(self) -> str: ...
    def device(self) -> AsyncDevice: ...
    async def wait(self, timeout: float | None = None) -> Self: ...
    def raw(self) -> dict[str, Any]: ...
    def yang(self) -> YangDataMapping: ...
    def status(self) -> NetconfResultStatus: ...

class YangDataMapping(dict[str, object]):
    name: Incomplete
    def __init__(self, name: str, data: dict[str, object]) -> None: ...

class YangDataSequence(list[YangDataMapping]):
    name: Incomplete
    def __init__(self, name: str, node: list[dict[str, object]], fields: dict[str, object]) -> None: ...
