import inspect
from typing import Callable, TypeVar, Generic

from pybind.emitters import Emitter, TriEmitter, BiEmitter, ValueEmitter
from pybind.observables import Observable, ValueObservable, BiObservable, TriObservable, Observer, \
    ValueObserver, BiObserver, TriObserver

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


def trim_and_call(listener: Callable, *parameters):
    parameter_count = count_non_default_parameters(listener)
    trimmed_parameters = parameters[:parameter_count]
    listener(*trimmed_parameters)


def count_non_default_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for param in parameters.values() if param.default == param.empty)


def assert_parameter_max_count(callable_: Callable, max_count: int) -> None:
    if count_non_default_parameters(callable_) > max_count:
        raise ValueError(f"Callable {callable_.__name__} has too many non-default parameters: "
                         f"{count_non_default_parameters(callable_)} > {max_count}")


class Event(Observable, Emitter):
    def __init__(self):
        self.listeners = []

    def observe(self, observer: Observer):
        self.listeners.append(observer)
        assert_parameter_max_count(observer, 0)
        return self

    def unobserve(self, observer: Observer):
        self.listeners.remove(observer)
        return self

    def __call__(self) -> None:
        for listener in self.listeners:
            listener()


class ValueEvent(Generic[_S], ValueObservable[_S], ValueEmitter[_S]):
    _observers: list[Observer | ValueObserver[_S]]

    def __init__(self):
        self._observers = []
        super().__init__()

    def observe(self, observer: Observer | ValueObserver[_T]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 1)

    def unobserve(self, observer: Observer | ValueObserver[_T]) -> None:
        self._observers.remove(observer)

    def __call__(self, value: _S) -> None:
        for listener in self._observers:
            trim_and_call(listener, value)


class BiEvent(Generic[_S, _T], BiObservable[_S, _T], BiEmitter[_S, _T]):
    _observers: list[Observer | ValueObserver[_S] | BiObserver[_S, _T]]

    def __init__(self):
        self._observers = []

    def observe(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 2)

    def unobserve(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U]) -> None:
        self._observers.remove(observer)

    def __call__(self, value_0: _S, value_1: _T) -> None:
        for listener in self._observers:
            trim_and_call(listener, value_0, value_1)


class TriEvent(Generic[_S, _T, _U], TriObservable[_S, _T, _U], TriEmitter[_S, _T, _U]):
    _observers: list[ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]]

    def __init__(self):
        self._observers = []

    def observe(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U] | TriObserver[_T, _U, _S]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 3)

    def unobserve(self, observer: Observer | ValueObserver[_T] | BiObserver[_T, _U] | TriObserver[_T, _U, _S]) -> None:
        self._observers.remove(observer)

    def __call__(self, value_0: _S, value_1: _T, value_2: _U) -> None:
        for listener in self._observers:
            trim_and_call(listener, value_0, value_1, value_2)
