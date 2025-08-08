from .client import Client
from collections.abc import Generator
from contextlib import contextmanager

__all__ = ['create_default_repl_scope']

@contextmanager
def create_default_repl_scope(client: Client) -> Generator[dict[str, object], None, None]: ...
