from .portal import Portal
from .sync_wrapper import SyncWrapper
from collections.abc import Callable, Coroutine
from dataclasses import InitVar, dataclass
from typing import Any, Generic, Literal
from typing_extensions import Concatenate, overload

__all__ = ['automap', 'autowrap', 'autowrap_coro', 'syncproperty']

@overload
def automap(method: Callable[Concatenate[_T_AsyncObj, _P], _T_untransformed]) -> Callable[Concatenate[SyncWrapper[_T_AsyncObj], _P], _T_untransformed]: ...
@overload
def automap(method: Callable[[_T_AsyncObj], _T_untransformed], *, as_property: Literal[True]) -> syncproperty[Any, _T_untransformed]: ...

@dataclass
class autowrap(Generic[_R, _WrapperResult]):
    wrapper: Callable[[_R, Portal], _WrapperResult]
    @overload
    def __call__(self, method: Callable[Concatenate[_T_AsyncObj, _P], _R]) -> Callable[Concatenate[SyncWrapper[_T_AsyncObj], _P], _WrapperResult]: ...
    @overload
    def __call__(self, method: Callable[[_T_AsyncObj], _R], *, as_property: Literal[True]) -> syncproperty[SyncWrapper[Any], _WrapperResult]: ...

@overload
def autowrap_coro(coro_method: Callable[Concatenate[_T_AsyncObj, _P], Coroutine[Any, Any, _R]]) -> Callable[Concatenate[SyncWrapper[_T_AsyncObj], _P], _R]: ...
@overload
def autowrap_coro(coro_method: Callable[Concatenate[_T_AsyncObj, _P], Coroutine[Any, Any, _R]], sync_wrapper: Callable[[_R, Portal], _WrapperResult]) -> Callable[Concatenate[SyncWrapper[_T_AsyncObj], _P], _WrapperResult]: ...

@dataclass
class syncproperty(Generic[_T, _R]):
    func: Callable[[_T], _R]
    doc: InitVar[str | None]
    annotations: InitVar[dict[str, str]]
    __doc__ = ...
    def __post_init__(self, doc: str | None, annotations: dict[str, str]) -> None: ...
    @overload
    def __get__(self, obj: None, objtype: None) -> syncproperty[_T, _R]: ...
    @overload
    def __get__(self, obj: _T, objtype: type[object]) -> _R: ...
    def __set__(self, obj: _T, value: _R) -> None: ...
