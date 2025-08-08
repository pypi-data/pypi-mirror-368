from ..from_async import SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.netconf.xpath_results import AsyncDeviceToSingleXPathResultDict, AsyncDeviceToXPathResultsDict, AsyncGetSingleXPathResult, AsyncGetXPathsResult, NetconfResultStatus as NetconfResultStatus, YangDataMapping as YangDataMapping, YangDataSequence as YangDataSequence
from typing_extensions import Self

__all__ = ['DeviceToXPathResultsDict', 'DeviceToSingleXPathResultDict', 'NetconfResultStatus', 'GetXPathsResult', 'GetSingleXPathResult', 'YangDataMapping', 'YangDataSequence']

class DeviceToXPathResultsDict(SyncDictWrapper[AsyncDeviceToXPathResultsDict, str, AsyncGetXPathsResult, 'GetXPathsResult']): ...
class DeviceToSingleXPathResultDict(SyncDictWrapper[AsyncDeviceToSingleXPathResultDict, str, AsyncGetSingleXPathResult, 'GetSingleXPathResult']): ...
class GetXPathsResult(SyncDictWrapper[AsyncGetXPathsResult, str, AsyncGetSingleXPathResult, 'GetSingleXPathResult']): ...

class GetSingleXPathResult(SyncWrapper[AsyncGetSingleXPathResult]):
    raw: Incomplete
    yang: Incomplete
    status: Incomplete
    device_name: Incomplete
    device: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
