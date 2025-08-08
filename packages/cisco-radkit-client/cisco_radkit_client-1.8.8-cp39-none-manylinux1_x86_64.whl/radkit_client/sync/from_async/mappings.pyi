from .portal import Portal
from _typeshed import Incomplete
from typing import Any

__all__ = ['TypesWithoutIO', 'types_without_io', 'wrap_any']

TypesWithoutIO: Incomplete
types_without_io: Incomplete

def wrap_any(value: object, portal: Portal) -> Any: ...
