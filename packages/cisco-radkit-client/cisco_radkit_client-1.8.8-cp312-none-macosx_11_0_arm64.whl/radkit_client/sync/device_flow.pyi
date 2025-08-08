from .exec import ExecResponse_ByDevice_ByCommand, ExecResponse_ByDevice_ToSingle
from .from_async import SyncWrapper
from _typeshed import Incomplete
from collections.abc import Sequence
from radkit_client.async_.device_flow import AsyncDeviceFlow, DeviceFlowFailedError as DeviceFlowFailedError, DeviceFlowMode as DeviceFlowMode
from radkit_common.terminal_interaction.prompt_detection import PromptDetectionStrategy
from re import Pattern
from typing import overload

__all__ = ['DeviceFlowMode', 'DeviceFlow', 'DeviceFlowFailedError']

class DeviceFlow(SyncWrapper[AsyncDeviceFlow]):
    active_devices: Incomplete
    failed_devices: Incomplete
    command_failed: Incomplete
    flow_mode: Incomplete
    @overload
    def exec_wait(self, commands: str, synced: bool = ..., timeout: int = ..., exec_error_patterns: Sequence[Pattern[str]] | None = None, prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> ExecResponse_ByDevice_ToSingle[str]: ...
    @overload
    def exec_wait(self, commands: list[str], synced: bool = ..., timeout: int = ..., exec_error_patterns: Sequence[Pattern[str]] | None = None, prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> ExecResponse_ByDevice_ByCommand[str]: ...
