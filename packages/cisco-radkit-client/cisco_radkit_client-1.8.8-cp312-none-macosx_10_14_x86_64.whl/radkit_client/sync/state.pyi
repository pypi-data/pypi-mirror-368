from .from_async import SyncDictWrapper
from .port_forwarding import TCPPortForwarder
from .request import AnySyncRequest
from .terminal import AnySyncTerminalConnection
from _typeshed import Incomplete
from pydantic import BaseModel
from radkit_client.async_.port_forwarding import AsyncTCPPortForwarder
from radkit_client.async_.request import AsyncBaseRequest
from radkit_client.async_.state import AsyncRequestsDict, AsyncSessionLog, AsyncSessionLogsDict, AsyncSessionsDict, AsyncTCPPortForwardsDict
from radkit_client.async_.terminal import AnyAsyncTerminalConnection
from radkit_client.sync.terminal.connection import SessionLog

__all__ = ['RequestsDict', 'SessionLogsDict', 'SessionsDict', 'TCPPortForwardsDict']

class RequestsDict(SyncDictWrapper[AsyncRequestsDict, int, AsyncBaseRequest[BaseModel, BaseModel, BaseModel], AnySyncRequest]):
    client: Incomplete

class SessionLogsDict(SyncDictWrapper[AsyncSessionLogsDict, int, AsyncSessionLog, SessionLog]):
    client: Incomplete

class SessionsDict(SyncDictWrapper[AsyncSessionsDict, int, AnyAsyncTerminalConnection, AnySyncTerminalConnection]):
    client: Incomplete

class TCPPortForwardsDict(SyncDictWrapper[AsyncTCPPortForwardsDict, int, AsyncTCPPortForwarder, TCPPortForwarder]):
    client: Incomplete
