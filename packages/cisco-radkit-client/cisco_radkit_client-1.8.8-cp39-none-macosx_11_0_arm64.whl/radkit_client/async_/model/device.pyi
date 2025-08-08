from .netconf import NetconfModel
from .swagger import SwaggerModel
from dataclasses import dataclass, field
from uuid import UUID

__all__ = ['DeviceModel']

@dataclass
class DeviceModel:
    uuid: UUID
    name: str
    service_display_name: str
    device_type: str
    internal_attrs: dict[str, object]
    metadata: dict[str, object] = field(default_factory=dict)
    ephemeral_attrs: dict[str, object] = field(default_factory=dict)
    swagger_model: SwaggerModel = field(default_factory=SwaggerModel)
    netconf_model: NetconfModel = field(default_factory=NetconfModel)
    failed: bool = ...
