from .device import AsyncDeviceDict
from .exceptions import ClientError
from .exec import AsyncExecResponse_ByDevice_ByCommand, AsyncExecResponse_ByDevice_ToSingle
from collections.abc import Sequence
from enum import Enum
from radkit_common.terminal_interaction.prompt_detection import PromptDetectionStrategy
from re import Pattern
from typing import overload

__all__ = ['DeviceFlowMode', 'DeviceFlowFailedError', 'AsyncDeviceFlow']

class DeviceFlowMode(Enum):
    BEST_EFFORT = 'BEST_EFFORT'
    AT_LEAST_1 = 'AT_LEAST_1'
    FULL_SUCCESS = 'FULL_SUCCESS'

class DeviceFlowFailedError(ClientError): ...

class AsyncDeviceFlow:
    def __init__(self, devices: AsyncDeviceDict, flow_mode: DeviceFlowMode = ..., exec_error_patterns: Sequence[Pattern[str]] | None = None) -> None: ...
    def active_devices(self) -> AsyncDeviceDict: ...
    def failed_devices(self) -> AsyncDeviceDict: ...
    def command_failed(self) -> AsyncDeviceDict: ...
    def flow_mode(self) -> DeviceFlowMode: ...
    @overload
    async def exec_wait(self, commands: str, timeout: int = ..., exec_error_patterns: Sequence[Pattern[str]] | None = None, prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> AsyncExecResponse_ByDevice_ToSingle[str]: ...
    @overload
    async def exec_wait(self, commands: list[str], timeout: int = ..., exec_error_patterns: Sequence[Pattern[str]] | None = None, prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> AsyncExecResponse_ByDevice_ByCommand[str]: ...
