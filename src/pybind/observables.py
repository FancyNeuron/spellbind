from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol
from weakref import WeakMethod, ref

from pybind.functions import count_positional_parameters

_SC = TypeVar("_SC", contravariant=True)
_TC = TypeVar("_TC", contravariant=True)
_UC = TypeVar("_UC", contravariant=True)

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")

_O = TypeVar('_O', bound=Callable)


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_TC]):
    def __call__(self, arg: _TC) -> None: ...


class BiObserver(Protocol[_TC, _UC]):
    def __call__(self, arg1: _TC, arg2: _UC) -> None: ...


class TriObserver(Protocol[_TC, _UC, _SC]):
    def __call__(self, arg1: _TC, arg2: _UC, arg3: _SC) -> None: ...


class DeadReferenceError(Exception):
    pass


class Subscription(Generic[_O], ABC):
    def __init__(self, observer: _O):
        self._positional_parameters = count_positional_parameters(observer)

    def _call(self, observer: _O, *args) -> None:
        trimmed_args = args[:self._positional_parameters]
        observer(*trimmed_args)

    @abstractmethod
    def __call__(self, *args) -> None:
        raise NotImplementedError

    @abstractmethod
    def matches_observer(self, observer: _O) -> bool:
        raise NotImplementedError


class StrongSubscription(Subscription[_O], Generic[_O]):
    def __init__(self, observer: _O):
        super().__init__(observer)
        self._observer = observer

    def __call__(self, *args) -> None:
        self._call(self._observer, *args)

    def matches_observer(self, observer: _O) -> bool:
        return self._observer == observer


class WeakSubscription(Subscription[_O], Generic[_O]):
    _ref: ref[_O] | WeakMethod

    def __init__(self, observer: _O):
        super().__init__(observer)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    def __call__(self, *args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        self._call(observer, *args)

    def matches_observer(self, observer: _O) -> bool:
        return self._ref() == observer


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def weak_observe(self, observer: Observer) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer) -> None:
        raise NotImplementedError


class ValueObservable(Generic[_S], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError


class BiObservable(Generic[_S, _T], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        raise NotImplementedError

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        raise NotImplementedError


class TriObservable(Generic[_S, _T, _U], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        raise NotImplementedError

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        raise NotImplementedError
