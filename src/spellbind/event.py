from typing import Callable, TypeVar, Generic, Iterable, Sequence

from spellbind.emitters import Emitter, TriEmitter, BiEmitter, ValueEmitter, ValuesEmitter
from spellbind.observables import Observable, ValueObservable, BiObservable, TriObservable, Observer, \
    ValueObserver, BiObserver, TriObserver, ValuesObserver, ValuesObservable, _BaseObservable, _BaseValuesObservable, \
    _SingleBaseObservable

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_O = TypeVar('_O', bound=Callable)


class Event(_BaseObservable[Observer], Observable, Emitter):
    def _get_parameter_count(self) -> int:
        return 0

    def __call__(self) -> None:
        self._emit_nothing()


class ValueEvent(Generic[_S], _SingleBaseObservable[Observer | ValueObserver[_S]], ValueObservable[_S], ValueEmitter[_S]):
    def _get_parameter_count(self) -> int:
        return 1

    def __call__(self, value: _S) -> None:
        self._emit_single(value)

    def emit_lazy(self, func: Callable[[], _S]) -> None:
        self._emit_single_lazy(func)


class BiEvent(Generic[_S, _T], _BaseObservable[Observer | ValueObserver[_S] | BiObserver[_S, _T]], BiObservable[_S, _T], BiEmitter[_S, _T]):
    def _get_parameter_count(self) -> int:
        return 2

    def __call__(self, value_0: _S, value_1: _T) -> None:
        self._emit_n((value_0, value_1))


class TriEvent(Generic[_S, _T, _U],
               _BaseObservable[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]],
               TriObservable[_S, _T, _U],
               TriEmitter[_S, _T, _U]):
    def _get_parameter_count(self) -> int:
        return 3

    def __call__(self, value_0: _S, value_1: _T, value_2: _U) -> None:
        self._emit_n((value_0, value_1, value_2))


class ValuesEvent(Generic[_S], _BaseValuesObservable[Observer | ValuesObserver[_S]], ValuesObservable[_S], ValuesEmitter[_S]):
    def __call__(self, value: Iterable[_S]) -> None:
        self._emit_single(value)

    def emit_single(self, value: _S) -> None:
        self._emit_single((value,))

    def emit_lazy(self, func: Callable[[], Sequence[_S]]) -> None:
        self._emit_single_lazy(func)
