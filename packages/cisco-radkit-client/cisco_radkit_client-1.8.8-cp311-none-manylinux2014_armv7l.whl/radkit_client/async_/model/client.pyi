from .integrations import IntegrationsModel
from .service import ServiceModel
from collections.abc import Sequence
from dataclasses import dataclass, field
from radkit_common.domains import Domain
from radkit_common.rpc import RPCFeatures, RPCName, RPCTarget

__all__ = ['ClientModel']

class _ServicesDict(dict[RPCTarget, ServiceModel]):
    def __missing__(self, key: RPCTarget) -> ServiceModel: ...

@dataclass
class ClientModel:
    default_domain: Domain
    services: dict[RPCTarget, ServiceModel] = field(default_factory=_ServicesDict)
    service_name_to_target: dict[str, RPCTarget] = field(default_factory=dict)
    integrations: IntegrationsModel = field(default_factory=IntegrationsModel)
    def get_capabilities_for_target(self, target: RPCTarget) -> Sequence[RPCName] | None: ...
    def get_rpc_features_for_target(self, target: RPCTarget, rpc_name: RPCName) -> RPCFeatures: ...
