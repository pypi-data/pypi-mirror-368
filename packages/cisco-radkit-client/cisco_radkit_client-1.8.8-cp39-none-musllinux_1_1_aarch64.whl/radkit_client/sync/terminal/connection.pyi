import concurrent.futures
from ..from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.state import AsyncSessionLog
from radkit_client.async_.terminal.connection import AsyncFileReadConnection, AsyncFileWriteConnection, AsyncInteractiveConnection, AsyncRemoteExecSequenceConnection, FileTransferStatus as FileTransferStatus, InteractiveConnectionStatus as InteractiveConnectionStatus, TerminalConnectionError as TerminalConnectionError
from radkit_common.identities import ServiceID
from typing import Generic
from typing_extensions import Self

__all__ = ['InteractiveConnection', 'InteractiveConnectionStatus', 'FileWriteConnection', 'FileReadConnection', 'AnySyncTerminalConnection', 'TerminalConnectionError', 'FileTransferStatus', 'InteractiveConnectionStatus']

class _TerminalConnection(SyncWrapper[_T_AsyncTerminalConnection], Generic[_T_AsyncTerminalConnection]):
    request: Incomplete
    closed: Incomplete
    at_eof: Incomplete
    bytes_read: Incomplete
    bytes_written: Incomplete
    client_id: Incomplete
    service_id: Incomplete
    device_name: Incomplete
    session_log_filepath: Incomplete
    session_log_filename: Incomplete
    session_log_rotate: Incomplete
    device: Incomplete
    service: Incomplete
    write_eof: Incomplete
    wait_closed: Incomplete
    close: Incomplete
    attach_socket: Incomplete
    detach_socket: Incomplete
    socket_forwarder: Incomplete
    def wait(self) -> Self: ...
    @property
    def result(self) -> Self: ...
    @property
    def serial(self) -> ServiceID | None: ...

class InteractiveConnection(_TerminalConnection[AsyncInteractiveConnection]):
    status: Incomplete
    attach: Incomplete
    write: Incomplete
    read: Incomplete
    readline: Incomplete
    readexactly: Incomplete
    readuntil: Incomplete
    readuntil_regex: Incomplete
    readuntil_timeout: Incomplete
    exec: Incomplete
    run_terminal_interaction: Incomplete
    run_exec_sequence: Incomplete
    run_remote_exec_sequence: Incomplete
    run_remote_exec_sequence_as_connection: Incomplete
    run_procedure: Incomplete
    run_remote_procedure: Incomplete
    def read_line(self, *, timeout: float | None = None) -> bytes: ...

class FileWriteConnection(_TerminalConnection[AsyncFileWriteConnection]):
    status: Incomplete
    params: Incomplete
    remote_path: Incomplete
    local_path: Incomplete
    abs_local_path: Incomplete
    show_progress: Incomplete
    write: Incomplete
    read: Incomplete
    readline: Incomplete
    readexactly: Incomplete
    readuntil: Incomplete
    readuntil_regex: Incomplete
    wait_transfer_done: Incomplete
    def start_upload(self, local_path: str) -> concurrent.futures.Future[None]: ...

class FileReadConnection(_TerminalConnection[AsyncFileReadConnection]):
    status: Incomplete
    params: Incomplete
    remote_path: Incomplete
    local_path: Incomplete
    abs_local_path: Incomplete
    show_progress: Incomplete
    write: Incomplete
    read: Incomplete
    readline: Incomplete
    readexactly: Incomplete
    readuntil: Incomplete
    readuntil_regex: Incomplete
    wait_transfer_done: Incomplete
    def read_line(self, *, timeout: float | None = None) -> bytes: ...

class RemoteExecSequenceConnection(_TerminalConnection[AsyncRemoteExecSequenceConnection]):
    read: Incomplete
    readline: Incomplete
    readexactly: Incomplete
    readuntil: Incomplete
    readuntil_regex: Incomplete
    def wait(self) -> Self: ...

class SessionLog(SyncWrapper[AsyncSessionLog]):
    id: Incomplete
    device_name: Incomplete
    filename: Incomplete
    filepath: Incomplete
    rotate: Incomplete
AnySyncTerminalConnection = InteractiveConnection | FileReadConnection | FileWriteConnection | RemoteExecSequenceConnection
