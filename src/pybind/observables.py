from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_T]):
    def __call__(self, arg: _T) -> None: ...


class BiObserver(Protocol[_T, _U]):
    def __call__(self, arg1: _T, arg2: _U) -> None: ...


class TriObserver(Protocol[_T, _U, _S]):
    def __call__(self, arg1: _T, arg2: _U, arg3: _S) -> None: ...


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer) -> None:
        raise NotImplementedError


class ValueObservable(Generic[_T], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_T]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_T]) -> None:
        raise NotImplementedError


class BiObservable(Generic[_T, _U], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U]) -> None:
        raise NotImplementedError


class TriObservable(Generic[_T, _U, _S], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U] | TriObserver[_T, _U, _S]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U] | TriObserver[_T, _U, _S]) -> None:
        raise NotImplementedError