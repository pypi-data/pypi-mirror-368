from dataclasses import dataclass
from radkit_common.domains import Domain
from radkit_common.identities import ClientID, Email, ServiceID

__all__ = ['ServiceEnrollInfo', 'ClientEnrollInfo']

@dataclass
class ServiceEnrollInfo:
    email: Email
    serial: ServiceID
    otp: str
    domain: Domain
    __pt_repr__ = ...
    def domain_name(self) -> str: ...

@dataclass
class ClientEnrollInfo:
    email: ClientID
    otp: str
    domain: Domain
    __pt_repr__ = ...
    def domain_name(self) -> str: ...
