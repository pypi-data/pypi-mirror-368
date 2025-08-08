from .from_async import SyncDictWrapper
from _typeshed import Incomplete
from collections.abc import Generator
from contextlib import contextmanager
from radkit_client.async_.joining import AsyncJoinedTasks, AsyncTask, JoinedTasksStatus as JoinedTasksStatus
from typing import Protocol
from typing_extensions import Self

__all__ = ['Task', 'JoinedTasks', 'join', 'JoinedTasksStatus']

class Task(Protocol): ...

class JoinedTasks(SyncDictWrapper[AsyncJoinedTasks, int, AsyncTask, Task]):
    show_progress: Incomplete
    def wait(self, timeout: float | None = None) -> Self: ...
    status: Incomplete
    done_count: Incomplete
    success_count: Incomplete
    failure_count: Incomplete
    def as_completed(self) -> Generator[Task, None, None]: ...

@contextmanager
def join(*awaitables: Task) -> Generator[JoinedTasks, None, None]: ...
