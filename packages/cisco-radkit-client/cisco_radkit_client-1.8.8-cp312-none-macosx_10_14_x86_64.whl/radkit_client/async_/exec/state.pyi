from ..request import AsyncSimpleRequest
from ..state import AsyncServiceState
from .status import ExecStatus
from _typeshed import Incomplete
from dataclasses import dataclass
from radkit_client.async_.model.device import DeviceModel
from radkit_common.identities import ServiceID
from radkit_common.protocol.device_actions import DeviceAction, DeviceActionPartialResponse
from radkit_common.protocol.exec import ExecCommands, ExecOutput
from radkit_common.protocol.upload_parameters import UploadParameters
from radkit_common.terminal_interaction.prompt_detection import PromptDetectionStrategy
from typing_extensions import TypeAlias
from uuid import UUID

__all__ = ['AsyncSimpleExecRequest', 'AsyncSingleExecState', 'AsyncExecState']

AsyncSimpleExecRequest: TypeAlias = AsyncSimpleRequest[DeviceAction[ExecCommands], DeviceActionPartialResponse[list[ExecOutput]], None]

@dataclass
class AsyncSingleExecState:
    record_id: int
    command: str
    service_id: ServiceID | None
    device_uuid: UUID
    device_model: DeviceModel
    sudo: bool
    request: AsyncSimpleExecRequest | None = ...
    returned_data: list[str] = ...
    errors: list[str] = ...
    done: bool = ...
    logger = ...
    exec_record = ...
    def __post_init__(self) -> None: ...
    def add_error(self, message: str) -> None: ...
    def add_data(self, data: str, done: bool = False) -> None: ...
    async def wait(self) -> None: ...
    def status(self) -> ExecStatus: ...

class AsyncExecState:
    service_state: Incomplete
    commands: Incomplete
    reset_before: Incomplete
    reset_after: Incomplete
    timeout: Incomplete
    upload_to: Incomplete
    device_uuids: Incomplete
    sudo: Incomplete
    prompt_detection_strategy: Incomplete
    devicename_to_uuid: Incomplete
    single_exec_states: Incomplete
    record_id_to_single_exec_state: Incomplete
    def __init__(self, service_state: AsyncServiceState, device_uuids: frozenset[UUID], commands: list[str], reset_before: bool = False, reset_after: bool = False, timeout: int = 0, upload_to: UploadParameters | None = None, sudo: bool = False, prompt_detection_strategy: PromptDetectionStrategy | None = None) -> None: ...
