from _typeshed import Incomplete
from dataclasses import dataclass
from pydantic import BaseModel
from radkit_client.async_.cloud_connections import AsyncCloudConnection
from radkit_client.async_.model.integrations import BDBPermissionsModel
from radkit_client.async_.state import AsyncClientState
from typing import Any

__all__ = ['AsyncBDB', 'BDBError', 'BDBPermissions']

class BDBError(Exception): ...

@dataclass(frozen=True)
class BDBTask:
    task: str
    description: str
    labels: list[str]
    service: str
    internal: bool
    external: bool
    blocked: bool

@dataclass(frozen=True)
class BDBTaskCode:
    url: str
    content: bytes

class BDBPermissions:
    def __init__(self, model: BDBPermissionsModel) -> None: ...
    @property
    def blocklist(self) -> set[str]: ...
    @property
    def internal(self) -> set[str]: ...
    @property
    def external(self) -> set[str]: ...
    def is_blocked(self, name: str) -> bool: ...
    def is_internal(self, name: str) -> bool: ...
    def is_external(self, name: str) -> bool: ...

class BDBTaskDict(dict[str, Any]):
    __pt_repr__: Incomplete

class _Task(BaseModel):
    name: str
    description: str
    labels: list[str]
    service: str

class _TaskList(BaseModel):
    data: list[_Task]

class DefaultFromSettings: ...

class AsyncBDB:
    def __init__(self, client_state: AsyncClientState) -> None: ...
    async def permissions(self, reload: bool = False, connection: AsyncCloudConnection | None = None) -> BDBPermissions: ...
    async def run_script(self, script: str, input: dict[str, str | int | float | bool] | None = None, asynchronous: bool = False, timeout: float | None | DefaultFromSettings = ..., connection: AsyncCloudConnection | None = None) -> Any: ...
    async def upload_file(self, filepath: str, connection: AsyncCloudConnection | None = None) -> None: ...
    async def upload_string_as_file(self, input: str, filename: str, connection: AsyncCloudConnection | None = None) -> None: ...
    async def get_tasks(self, labels: list[str] | None = None, service: str = 'radkit3.9', connection: AsyncCloudConnection | None = None) -> BDBTaskDict: ...
    async def get_task_code(self, task_name: str, file_name: str = '__init__.py', connection: AsyncCloudConnection | None = None) -> BDBTaskCode: ...
    async def get_task_meta(self, task_name: str, connection: AsyncCloudConnection | None = None) -> Any: ...
