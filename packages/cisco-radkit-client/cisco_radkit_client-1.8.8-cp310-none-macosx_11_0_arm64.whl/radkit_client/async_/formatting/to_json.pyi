from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

__all__ = ['std_object_to_json', 'to_std_object', 'ToStdObject']

def std_object_to_json(obj: object, **kwargs: Any) -> str: ...
def to_std_object(obj: object) -> object: ...

@dataclass
class ToStdObject:
    fields: Sequence[str] = field(default_factory=list)
    def __get__(self, obj: _T, objtype: _T | None = None) -> Callable[[], Any]: ...
