from _typeshed import Incomplete
from radkit_client.async_.exceptions import ClientError as ClientError

class CXDError(ClientError):
    message: Incomplete
    def __init__(self, message: str | None = None) -> None: ...

class RADKitClientTypeNotSupportedError(CXDError):
    message: str

class CXDBadPayloadError(CXDError):
    message: str

class CXDAuthenticationFailedError(CXDError):
    message: str

class CXDAuthorizationFailedError(CXDError):
    message: str

class CXDTargetExistsError(CXDError):
    message: str

class CXDTargetNotFoundError(CXDError):
    message: str

class CXDTargetInvalid(CXDError):
    message: str

class CXDInternalError(CXDError):
    message: str

class CXDUnsupportedProtocolError(CXDError):
    message: str

class CXDConnectionTimeoutError(CXDError):
    message: str

class CXDTokenExpirationUnsetError(CXDError):
    message: str

class CXDAuthenticatorNotSetError(CXDError):
    message: str

class CXDTargetNotSetError(CXDError):
    message: str

class CXDDestinationNameNotSetError(CXDError):
    message: str

class CXDLocalNameAndDataSetError(CXDError):
    message: str

class CXDLocalNameNotFoundError(CXDError):
    message: str

class CXDTargetInvalidFormat(CXDError):
    message: str
