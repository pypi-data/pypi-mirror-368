from _typeshed import Incomplete
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from radkit_common.protocol import swagger as swagger_protocol
from typing import Any

__all__ = ['HttpVerb', 'SwaggerAPIStatus', 'SwaggerPathOperationParameterModel', 'SwaggerPathOperationModel', 'SwaggerPathModel', 'SwaggerModel']

HttpVerb: Incomplete

class SwaggerAPIStatus(Enum):
    UNKNOWN = 'UNKNOWN'
    NO_CONFIG = 'NO_CONFIG'
    CONFIGURED = 'CONFIGURED'
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'

@dataclass
class SwaggerPathOperationParameterModel:
    name: str
    required: bool
    location: str
    description: str
    @property
    def alias(self) -> str: ...

@dataclass
class SwaggerPathOperationModel:
    description: str
    parameters: Sequence[SwaggerPathOperationParameterModel]
    def __post_init__(self) -> None: ...

@dataclass
class SwaggerPathModel:
    path: str
    operations: Mapping[HttpVerb, SwaggerPathOperationModel]

@dataclass
class SwaggerModel:
    status: SwaggerAPIStatus = ...
    status_message: str = ...
    paths: dict[str, SwaggerPathModel] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    def process_swagger_paths(self, swagger_paths: swagger_protocol.SwaggerPaths) -> None: ...
