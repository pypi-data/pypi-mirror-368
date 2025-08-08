from .from_async import SyncWrapper
from _typeshed import Incomplete
from radkit_client.async_.ssh_forwarding import AsyncProxySshForwarder, AsyncSshConnection, AsyncSshConnectionsDict, AsyncSshHostKeyPair, AsyncSshSession, AsyncSshSessionsDict
from radkit_client.sync.from_async.sync_wrapper import SyncDictWrapper

__all__ = ['ProxySshForwarder', 'SshConnections', 'SshConnection', 'SshSessions', 'SshSession']

class SshSession(SyncWrapper[AsyncSshSession]):
    status: Incomplete
    request_type: Incomplete
    term: Incomplete
    term_size: Incomplete
    pty_requested: Incomplete
    exception: Incomplete

class SshSessions(SyncDictWrapper[AsyncSshSessionsDict, int, AsyncSshSession, SshSession]): ...

class SshConnection(SyncWrapper[AsyncSshConnection]):
    device_name: Incomplete
    service_name: Incomplete
    status: Incomplete
    exception: Incomplete
    sessions: Incomplete

class SshConnections(SyncDictWrapper[AsyncSshConnectionsDict, int, AsyncSshConnection, SshConnection]): ...

class SshHostKeyPair(SyncWrapper[AsyncSshHostKeyPair]):
    public_key: Incomplete
    private_key: Incomplete
    fingerprint_md5: Incomplete
    fingerprint_sha256: Incomplete

class ProxySshForwarder(SyncWrapper[AsyncProxySshForwarder]):
    status: Incomplete
    requested_port: Incomplete
    requested_host: Incomplete
    addresses: Incomplete
    start: Incomplete
    stop: Incomplete
    fingerprint_md5: Incomplete
    fingerprint_sha256: Incomplete
    host_key_pair: Incomplete
    connections: Incomplete
