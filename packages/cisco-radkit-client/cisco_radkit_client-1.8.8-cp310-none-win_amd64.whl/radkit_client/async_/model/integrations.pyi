from _typeshed import Incomplete
from dataclasses import dataclass, field
from radkit_common.domains import Domain
from radkit_common.identities import ClientID

__all__ = ['IntegrationsModel', 'BDBModel', 'BDBPermissionsModel']

@dataclass
class IntegrationsModel:
    bdb: BDBModel = field(default_factory=Incomplete)

@dataclass
class BDBModel:
    permissions: dict[tuple[Domain, ClientID], BDBPermissionsModel] = field(default_factory=dict)

@dataclass
class BDBPermissionsModel:
    blocklist: set[str]
    internal: set[str]
    external: set[str]
