from .exec import ExecResponse_ByCommand_ToSingle, ExecResponse_ByDevice_ByCommand, ExecResponse_ByDevice_ToSingle, SingleExecResponse
from .from_async import SyncDictWrapper, SyncWrapper
from .request import FillerRequest
from _typeshed import Incomplete
from collections.abc import Iterable, Sequence
from radkit_client.async_.device import AsyncDevice, AsyncDeviceAttributes, AsyncDeviceAttributesDict, AsyncDeviceCapabilitiesUpdate, AsyncDeviceDict, AsyncDeviceDictCapabilitiesUpdate, AsyncDeviceParameters, AsyncEphemeralDeviceAttributesDict, DeviceCapabilitiesUpdateStatus as DeviceCapabilitiesUpdateStatus, DeviceDictCapabilitiesUpdateStatus as DeviceDictCapabilitiesUpdateStatus
from radkit_common.identities import ServiceID
from radkit_common.protocol.device_actions import DeviceAction, DeviceActionPartialResponse
from radkit_common.protocol.terminal import ReadAndUploadFile
from radkit_common.protocol.upload_parameters import UploadParameters
from radkit_common.rpc.definition import NOTHING
from radkit_common.terminal_interaction.prompt_detection import PromptDetectionStrategy
from typing import overload
from typing_extensions import Self
from uuid import UUID

__all__ = ['DeviceDict', 'Device', 'DeviceAttributes', 'EphemeralDeviceAttributesDict', 'DeviceAttributesDict', 'DeviceCapabilitiesUpdate', 'DeviceDictCapabilitiesUpdate', 'DeviceCapabilitiesUpdateStatus', 'DeviceDictCapabilitiesUpdateStatus']

class EphemeralDeviceAttributesDict(SyncDictWrapper[AsyncEphemeralDeviceAttributesDict, str, object, object]):
    __setitem__: Incomplete
    __delitem__: Incomplete
    def get(self, /, __key: str, default: object = None) -> object: ...
    @overload
    def update(self, other: tuple[str, object], **kwargs: object) -> None: ...
    @overload
    def update(self, other: Iterable[tuple[str, object]], **kwargs: object) -> None: ...
    @overload
    def update(self, **kwargs: object) -> None: ...
    pop: Incomplete
    popitem: Incomplete
    clear: Incomplete
    setdefault: Incomplete
    device_name: Incomplete
    device: Incomplete

class DeviceAttributesDict(SyncDictWrapper[AsyncDeviceAttributesDict, str, object, object]):
    device_name: Incomplete
    device: Incomplete

class DeviceAttributes(SyncWrapper[AsyncDeviceAttributes]):
    internal: Incomplete
    metadata: Incomplete
    @property
    def external(self) -> DeviceAttributesDict: ...
    ephemeral: Incomplete
    device_name: Incomplete
    device: Incomplete

class DeviceParameters(SyncWrapper[AsyncDeviceParameters]):
    service_name: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    uuid: Incomplete
    name: Incomplete
    dev_id: Incomplete
    @property
    def serial(self) -> ServiceID | None: ...

class Device(SyncWrapper[AsyncDevice]):
    service: Incomplete
    client: Incomplete
    name: Incomplete
    service_display_name: Incomplete
    attributes: Incomplete
    host: Incomplete
    device_type: Incomplete
    forwarded_tcp_ports: Incomplete
    failed: Incomplete
    params: Incomplete
    session_logs: Incomplete
    sessions: Incomplete
    requests: Incomplete
    port_forwards: Incomplete
    swagger: Incomplete
    netconf: Incomplete
    snmp: Incomplete
    http: Incomplete
    singleton: Incomplete
    update_attributes: Incomplete
    interactive: Incomplete
    terminal: Incomplete
    forward_tcp_port: Incomplete
    set_failed: Incomplete
    update_swagger: Incomplete
    update_netconf: Incomplete
    scp_download_to_stream: Incomplete
    sftp_download_to_stream: Incomplete
    scp_download_to_file: Incomplete
    sftp_download_to_file: Incomplete
    scp_to_destination: Incomplete
    sftp_to_destination: Incomplete
    scp_upload_from_stream: Incomplete
    sftp_upload_from_stream: Incomplete
    scp_upload_from_file: Incomplete
    sftp_upload_from_file: Incomplete
    @overload
    def exec(self, commands: str, timeout: int = ..., upload_to: UploadParameters | None = ..., reset_before: bool = ..., reset_after: bool = ..., sudo: bool = ..., prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> SingleExecResponse[str]: ...
    @overload
    def exec(self, commands: list[str], timeout: int = ..., upload_to: UploadParameters | None = ..., reset_before: bool = ..., reset_after: bool = ..., sudo: bool = ..., prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> ExecResponse_ByCommand_ToSingle[str]: ...
    create_device_flow: Incomplete

class DeviceDict(SyncDictWrapper[AsyncDeviceDict, str, AsyncDevice, Device]):
    def __setitem__(self, name: str, device: Device) -> None: ...
    __delitem__: Incomplete
    status: Incomplete
    service: Incomplete
    client: Incomplete
    touched: Incomplete
    def remove(self, obj: UUID | str | Device | Sequence[UUID | str | Device] | DeviceDict) -> None: ...
    def add(self, obj: UUID | str | Device | Sequence[UUID | str | Device] | DeviceDict) -> None: ...
    clone: Incomplete
    copy: Incomplete
    filter: Incomplete
    exclude_failed: Incomplete
    def subset(self, devices: Iterable[str | UUID | Device]) -> DeviceDict: ...
    def __eq__(self, other: object) -> bool: ...
    def union(self, other: DeviceDict) -> DeviceDict: ...
    def difference(self, other: DeviceDict) -> DeviceDict: ...
    def intersection(self, other: DeviceDict) -> DeviceDict: ...
    def symmetric_difference(self, other: DeviceDict) -> DeviceDict: ...
    def issubset(self, other: DeviceDict) -> bool: ...
    def issuperset(self, other: DeviceDict) -> bool: ...
    __and__ = intersection
    __or__ = union
    __sub__ = difference
    __xor__ = symmetric_difference
    __le__ = issubset
    __ge__ = issuperset
    def __lt__(self, other: DeviceDict) -> bool: ...
    def __gt__(self, other: DeviceDict) -> bool: ...
    update_attributes: Incomplete
    update_swagger: Incomplete
    update_netconf: Incomplete
    netconf: Incomplete
    snmp: Incomplete
    session_logs: Incomplete
    sessions: Incomplete
    requests: Incomplete
    port_forwards: Incomplete
    create_device_flow: Incomplete
    @overload
    def exec(self, commands: str, *, timeout: int = ..., synced: bool = ..., upload_to: UploadParameters | None = ..., reset_before: bool = ..., sudo: bool = ..., prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> ExecResponse_ByDevice_ToSingle[str]: ...
    @overload
    def exec(self, commands: list[str], *, timeout: int = ..., synced: bool = ..., upload_to: UploadParameters | None = ..., reset_before: bool = ..., sudo: bool = ..., prompt_detection_strategy: PromptDetectionStrategy | None = ...) -> ExecResponse_ByDevice_ByCommand[str]: ...
    def scp_to_destination(self, remote_path: str, upload_parameters: UploadParameters) -> FillerRequest[DeviceAction[ReadAndUploadFile], DeviceActionPartialResponse[NOTHING], None]: ...
    def sftp_to_destination(self, remote_path: str, upload_parameters: UploadParameters) -> FillerRequest[DeviceAction[ReadAndUploadFile], DeviceActionPartialResponse[NOTHING], None]: ...

class DeviceCapabilitiesUpdate(SyncWrapper[AsyncDeviceCapabilitiesUpdate]):
    device_name: Incomplete
    device: Incomplete
    service_id: Incomplete
    result: Incomplete
    status: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...

class DeviceDictCapabilitiesUpdate(SyncDictWrapper[AsyncDeviceDictCapabilitiesUpdate, str, AsyncDeviceCapabilitiesUpdate, DeviceCapabilitiesUpdate]):
    service_id: Incomplete
    devices: Incomplete
    status: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
