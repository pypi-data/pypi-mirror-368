from dataclasses import dataclass
from enum import Enum
from typing import Any

__all__ = ['NetconfModel', 'NetconfStatus']

class NetconfStatus(Enum):
    UNKNOWN = 'UNKNOWN'
    AVAILABLE = 'AVAILABLE'
    NO_CONFIG = 'NO_CONFIG'
    UNAVAILABLE = 'UNAVAILABLE'

@dataclass
class NetconfModel:
    status: NetconfStatus = ...
    capabilities_raw: dict[str, Any] | None = ...
    capabilities_hash: str | None = ...
    all_namespaces: dict[str, str] | None = ...
    def process_capabilities_response(self, capabilities: dict[str, Any]) -> None: ...
