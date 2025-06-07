from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol


_SC = TypeVar("_SC", contravariant=True)
_TC = TypeVar("_TC", contravariant=True)
_UC = TypeVar("_UC", contravariant=True)

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_TC]):
    def __call__(self, arg: _TC) -> None: ...


class BiObserver(Protocol[_TC, _UC]):
    def __call__(self, arg1: _TC, arg2: _UC) -> None: ...


class TriObserver(Protocol[_TC, _UC, _SC]):
    def __call__(self, arg1: _TC, arg2: _UC, arg3: _SC) -> None: ...


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer) -> None:
        raise NotImplementedError


class ValueObservable(Generic[_S], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError


class BiObservable(Generic[_S, _T], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        raise NotImplementedError


class TriObservable(Generic[_S, _T, _U], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        raise NotImplementedError
