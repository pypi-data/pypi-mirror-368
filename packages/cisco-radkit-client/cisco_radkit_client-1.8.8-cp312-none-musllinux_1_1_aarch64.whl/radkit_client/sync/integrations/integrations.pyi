from ..from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.integrations import AsyncIntegrations

__all__ = ['Integrations']

class Integrations(SyncWrapper[AsyncIntegrations]):
    csone: Incomplete
    bdb: Incomplete
    cxd: Incomplete
