from _typeshed import Incomplete
from dataclasses import dataclass
from typing import Generic

__all__ = ['Id', 'AutoIncrementingIdGenerator', 'AutoIncrementingIdForHashableGenerator']

Id: Incomplete

@dataclass
class AutoIncrementingIdGenerator:
    def next(self) -> Id: ...

@dataclass
class AutoIncrementingIdForHashableGenerator(Generic[_T]):
    def get_id(self, obj: _T) -> Id: ...
    def lookup(self, id: Id) -> _T | None: ...
