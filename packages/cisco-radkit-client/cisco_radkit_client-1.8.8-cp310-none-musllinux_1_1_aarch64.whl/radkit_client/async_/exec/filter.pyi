from .status import ExecStatus
from collections.abc import Mapping
from dataclasses import dataclass
from radkit_common.identities import ServiceID
from typing import Any, Generic, Protocol
from typing_extensions import TypeAlias
from uuid import UUID

__all__ = ['ExecRecord', 'ExecFilterFunction', 'ExecSortFunction', 'ExecMapFunction', 'Sortable']

@dataclass(frozen=True)
class ExecRecord(Generic[_DataType]):
    command: str
    sudo: bool
    service_id: ServiceID | None
    device_uuid: UUID
    device_name: str
    device_type: str
    device_attributes_internal: Mapping[str, object]
    device_attributes_metadata: Mapping[str, object]
    device_attributes_ephemeral: Mapping[str, object]
    @property
    def raw_data(self) -> str: ...
    @property
    def data(self) -> _DataType: ...
    @property
    def status(self) -> ExecStatus: ...

class ExecFilterFunction(Protocol[_DataType]):
    def __call__(self, entry: ExecRecord[_DataType], /) -> bool: ...

class ExecMapFunction(Protocol[_DataType, _DataType2]):
    def __call__(self, entry: ExecRecord[_DataType], /) -> _DataType2: ...

class _SupportsDunderLT(Protocol):
    def __lt__(self, other: Any) -> bool: ...

class _SupportsDunderGT(Protocol):
    def __gt__(self, other: Any) -> bool: ...

Sortable: TypeAlias

class ExecSortFunction(Protocol[_DataType]):
    def __call__(self, entry: ExecRecord[_DataType], /) -> Sortable: ...
