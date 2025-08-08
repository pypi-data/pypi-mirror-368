from .client import Client as Client
from .service import Service as Service
from _typeshed import Incomplete
from collections.abc import Iterator
from contextlib import contextmanager
from radkit_client import licensing as licensing
from radkit_client.async_.exceptions import ClientError as ClientError
from radkit_client.async_.settings import get_settings as get_settings
from radkit_client.version import version_str as version_str

FULL_VERSION: Incomplete
VERSION_BANNER: Incomplete

class InteractiveError(ClientError): ...

@contextmanager
def connect_to_service(service_sn: str, sso_email: str | None = None, cert_identity: str | None = None, ca_path: str | None = None, cert_path: str | None = None, key_path: str | None = None, domain: str | None = None) -> Iterator[tuple[Client, Service]]: ...
def start_interactive(service: Service, device_name: str) -> None: ...
def main(service_sn: str, device_name: str | None, show_inventory: bool, sso_email: str | None, cert_identity: str | None, ca_path: str | None, cert_path: str | None, key_path: str | None, domain: str | None, debug: bool, tracebacks: bool, non_canonical: bool) -> int: ...
