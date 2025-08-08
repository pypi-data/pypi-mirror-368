import re
from .client import Client
from .integrations import CXD
from _typeshed import Incomplete
from asn1crypto import core
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, overload

__all__ = ['get_all_pipes', 'PIPE_DISPLAY_DICT', 'PIPE_COMPLETE_KEYS', 'PIPES_COMPLETE_META', 'grep', 'regrep', 'head', 'tail', 'sort', 'print', 'to_json', 'from_json', 'to_dict', 'read_from_file', 'write_to_file', 'append_to_file', 'encrypt', 'decrypt', 'encrypt_openssl', 'decrypt_openssl', 'to_base64', 'from_base64']

@dataclass
class Grep:
    keyword: str
    ignore_case: bool = ...
    inverse: bool = ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class ReGrep:
    regex: str
    inverse: bool = ...
    flags: re.RegexFlag = ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class Head:
    count: int = ...
    def __call__(self, count: int = 10) -> Head: ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class Tail:
    count: int = ...
    def __call__(self, count: int = 10) -> Tail: ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class Sort:
    reverse: bool = ...
    def __call__(self, reverse: bool = False) -> Sort: ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class ToJSON:
    dumps_args: Mapping[str, Any] = field(default_factory=Incomplete)
    def __call__(self, **kwargs: Mapping[str, Any]) -> ToJSON: ...
    def __ror__(self, other: object) -> str: ...

@dataclass
class FromJSON:
    loads_args: Mapping[str, Any] = field(default_factory=Incomplete)
    def __call__(self, **kwargs: Mapping[str, Any]) -> FromJSON: ...
    def __ror__(self, other: object) -> object: ...

@dataclass
class ToDict:
    recursive: bool = ...
    def __call__(self, recursive: bool = False) -> ToDict: ...
    def __ror__(self, other: object) -> object: ...

@dataclass
class Print:
    def __post_init__(self) -> None: ...
    def __call__(self, *values: object, sep: str = ' ', end: str = '\n') -> None: ...
    def __ror__(self, other: object) -> None: ...

@dataclass
class WriteToFile:
    file_path: Path
    def __post_init__(self) -> None: ...
    def __ror__(self, other: object) -> FileOperationSuccess | FileOperationFailure: ...

@dataclass
class AppendToFile:
    file_path: Path
    def __post_init__(self) -> None: ...
    def __ror__(self, other: object) -> FileOperationSuccess | FileOperationFailure: ...

@dataclass
class UploadToCXD:
    cxd_client: CXD = field(repr=False)
    target_id: str
    destination_file_name: str
    def __ror__(self, other: object) -> str: ...

@dataclass
class Encrypt:
    key: str
    salt_key: bool = ...
    def __call__(self, data: str) -> bytes: ...
    def __ror__(self, other: object) -> bytes: ...

@dataclass
class Decrypt:
    key: str
    def __call__(self, data: bytes) -> bytes: ...
    def __ror__(self, other: object) -> bytes: ...

@dataclass
class EncryptOpenSSL:
    key: str
    salt_size: int = ...
    iterations: int = ...
    def __ror__(self, other: object) -> bytes: ...

@dataclass
class DecryptOpenSSL:
    key: str
    salt_size: int = ...
    iterations: int = ...
    def __ror__(self, other: object) -> bytes: ...

@dataclass
class ToBase64:
    def __ror__(self, other: object) -> str: ...

@dataclass
class FromBase64:
    def __ror__(self, other: object) -> bytes: ...

@dataclass
class FileOperationSuccess:
    message: str

@dataclass
class FileOperationFailure:
    message: str
    exception: Exception

@overload
def read_from_file(file_path: Path | str, *, text: Literal[False] = False) -> bytes | FileOperationFailure: ...
@overload
def read_from_file(file_path: Path | str, *, text: Literal[True], encoding: str = ...) -> str | FileOperationFailure: ...

class EncryptionParameters(core.Sequence): ...
class EncryptionParametersSalt(core.Sequence): ...
grep = Grep
regrep = ReGrep
head: Incomplete
tail: Incomplete
sort: Incomplete
print: Incomplete
to_json: Incomplete
from_json: Incomplete
to_dict: Incomplete
write_to_file = WriteToFile
append_to_file = AppendToFile
encrypt = Encrypt
decrypt = Decrypt
encrypt_openssl = EncryptOpenSSL
decrypt_openssl = DecryptOpenSSL
to_base64: Incomplete
from_base64: Incomplete

def get_all_pipes(client: Client) -> dict[str, object]: ...

PIPE_DISPLAY_DICT: Incomplete
PIPE_COMPLETE_KEYS: Incomplete
PIPES_COMPLETE_META: Incomplete
