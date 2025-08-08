from ..from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.netconf.netconf_api import AsyncNetconfAPI, AsyncNetconfCapabilities, AsyncSingleDeviceNetconfAPI, NetconfAPIStatus as NetconfAPIStatus, XPathSplitter as XPathSplitter

__all__ = ['NetconfCapabilities', 'NetconfAPIStatus', 'NetconfAPI', 'SingleDeviceNetconfAPI', 'XPathSplitter']

class NetconfCapabilities(SyncWrapper[AsyncNetconfCapabilities]):
    raw: Incomplete
    namespaces: Incomplete
    hash: Incomplete

class NetconfAPI(SyncWrapper[AsyncNetconfAPI]):
    status: Incomplete
    yang: Incomplete
    capabilities: Incomplete
    get_xpaths: Incomplete

class SingleDeviceNetconfAPI(SyncWrapper[AsyncSingleDeviceNetconfAPI]):
    status: Incomplete
    yang: Incomplete
    capabilities: Incomplete
    get_xpaths: Incomplete
