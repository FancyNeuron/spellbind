import inspect
from inspect import Parameter
from typing import Callable, TypeVar, Generic

from pybind.emitters import Emitter, TriEmitter, BiEmitter, ValueEmitter
from pybind.observables import Observable, ValueObservable, BiObservable, TriObservable, Observer, \
    ValueObserver, BiObserver, TriObserver

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


def _is_positional_parameter(param: Parameter) -> bool:
    return param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)


def count_total_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for parameter in parameters.values() if _is_positional_parameter(parameter))


def trim_and_call(observer: Callable, *parameters):
    parameter_count = count_total_parameters(observer)
    trimmed_parameters = parameters[:parameter_count]
    observer(*trimmed_parameters)


def _is_required_positional_parameter(param: Parameter) -> bool:
    return param.default == param.empty and _is_positional_parameter(param)


def count_non_default_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for param in parameters.values() if _is_required_positional_parameter(param))


def assert_parameter_max_count(callable_: Callable, max_count: int) -> None:
    if count_non_default_parameters(callable_) > max_count:
        if hasattr(callable_, '__name__'):
            callable_name = callable_.__name__
        elif hasattr(callable_, '__class__'):
            callable_name = callable_.__class__.__name__
        else:
            callable_name = str(callable_)
        raise ValueError(f"Callable {callable_name} has too many non-default parameters: "
                         f"{count_non_default_parameters(callable_)} > {max_count}")


class Event(Observable, Emitter):
    _observers: list[Observer]

    def __init__(self):
        self._observers = []

    def observe(self, observer: Observer) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 0)

    def unobserve(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def __call__(self) -> None:
        for observer in self._observers:
            observer()


class ValueEvent(Generic[_S], ValueObservable[_S], ValueEmitter[_S]):
    _observers: list[Observer | ValueObserver[_S]]

    def __init__(self):
        self._observers = []
        super().__init__()

    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 1)

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        self._observers.remove(observer)

    def __call__(self, value: _S) -> None:
        for observer in self._observers:
            trim_and_call(observer, value)


class BiEvent(Generic[_S, _T], BiObservable[_S, _T], BiEmitter[_S, _T]):
    _observers: list[Observer | ValueObserver[_S] | BiObserver[_S, _T]]

    def __init__(self):
        self._observers = []

    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 2)

    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        self._observers.remove(observer)

    def __call__(self, value_0: _S, value_1: _T) -> None:
        for observer in self._observers:
            trim_and_call(observer, value_0, value_1)


class TriEvent(Generic[_S, _T, _U], TriObservable[_S, _T, _U], TriEmitter[_S, _T, _U]):
    _observers: list[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]]

    def __init__(self):
        self._observers = []

    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        self._observers.append(observer)
        assert_parameter_max_count(observer, 3)

    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        self._observers.remove(observer)

    def __call__(self, value_0: _S, value_1: _T, value_2: _U) -> None:
        for observer in self._observers:
            trim_and_call(observer, value_0, value_1, value_2)
