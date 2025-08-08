from ..from_async import SyncDictWrapper
from _typeshed import Incomplete
from radkit_client.async_.netconf.yang_model import AsyncSingleDeviceYangNode, AsyncYangNode

__all__ = ['YangNode', 'SingleDeviceYangNode']

class YangNode(SyncDictWrapper[AsyncYangNode, str, AsyncYangNode, 'YangNode']):
    name: Incomplete
    devices: Incomplete
    xpath: Incomplete
    namespaces: Incomplete
    get: Incomplete

class SingleDeviceYangNode(SyncDictWrapper[AsyncSingleDeviceYangNode, str, AsyncSingleDeviceYangNode, 'SingleDeviceYangNode']):
    name: Incomplete
    device_name: Incomplete
    xpath: Incomplete
    namespaces: Incomplete
    device: Incomplete
    get: Incomplete
