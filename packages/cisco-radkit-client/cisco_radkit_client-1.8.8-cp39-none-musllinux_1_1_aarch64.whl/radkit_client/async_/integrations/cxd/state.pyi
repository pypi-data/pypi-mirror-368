from .authenticators import AnyAsyncCXDAuthenticator
from .targets import AnyAsyncCXDTarget
from dataclasses import dataclass, field

__all__ = ['CXDState']

@dataclass
class CXDState:
    targets: dict[str, AnyAsyncCXDTarget] = field(default_factory=dict)
    default_authenticator: AnyAsyncCXDAuthenticator | None = ...
    default_target: str | None = ...
