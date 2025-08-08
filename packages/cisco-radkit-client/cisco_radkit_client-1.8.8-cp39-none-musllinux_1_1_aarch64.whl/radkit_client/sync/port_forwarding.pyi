from .from_async import SyncDictWrapper, SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.port_forwarding import AsyncConnection, AsyncConnections, AsyncEndpointConnections, AsyncEndpointConnectionsDict, AsyncProxyPortForwarder, AsyncTCPPortForwarder, ConnectionStatus as ConnectionStatus, PortForwarderInvalidStateError as PortForwarderInvalidStateError, PortForwarderStatus as PortForwarderStatus, ProxyAlreadyStartedError as ProxyAlreadyStartedError

__all__ = ['TCPPortForwarder', 'PortForwarderStatus', 'ProxyPortForwarder', 'PortForwarderInvalidStateError', 'ProxyAlreadyStartedError', 'Connection', 'Connections', 'EndpointConnections', 'EndpointConnectionsDict', 'ConnectionStatus']

class Connection(SyncWrapper[AsyncConnection]):
    uuid: Incomplete
    endpoint: Incomplete
    status: Incomplete
    opened: Incomplete
    closed: Incomplete
    exception: Incomplete

class Connections(SyncDictWrapper[AsyncConnections, int, AsyncConnection, Connection]): ...

class EndpointConnections(SyncWrapper[AsyncEndpointConnections]):
    connections: Incomplete

class EndpointConnectionsDict(SyncDictWrapper[AsyncEndpointConnectionsDict, str, AsyncEndpointConnections, EndpointConnections]): ...

class TCPPortForwarder(SyncWrapper[AsyncTCPPortForwarder]):
    status: Incomplete
    device: Incomplete
    device_name: Incomplete
    local_port: Incomplete
    destination_port: Incomplete
    start: Incomplete
    stop: Incomplete
    bytes_uploaded: Incomplete
    bytes_downloaded: Incomplete
    connections: Incomplete
    get_dynamic_local_ports: Incomplete

class ProxyPortForwarder(SyncWrapper[AsyncProxyPortForwarder]):
    status: Incomplete
    start: Incomplete
    stop: Incomplete
    bytes_uploaded: Incomplete
    bytes_downloaded: Incomplete
    exception: Incomplete
    connections: Incomplete
    endpoint_connections: Incomplete
    add_procedure: Incomplete
