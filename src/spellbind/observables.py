from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol, Iterable, Any, Sequence
from weakref import WeakMethod, ref

from spellbind.functions import count_positional_parameters, assert_parameter_max_count

_SC = TypeVar("_SC", contravariant=True)
_TC = TypeVar("_TC", contravariant=True)
_UC = TypeVar("_UC", contravariant=True)
_IC = TypeVar("_IC", bound=Iterable, contravariant=True)

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_I = TypeVar("_I", bound=Iterable)

_S_co = TypeVar("_S_co", covariant=True)

_O = TypeVar('_O', bound=Callable)


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_SC]):
    def __call__(self, arg: _SC, /) -> None: ...


class ValuesObserver(Protocol[_SC]):
    def __call__(self, args: Iterable[_SC], /) -> None: ...


class BiObserver(Protocol[_SC, _TC]):
    def __call__(self, arg1: _SC, arg2: _TC, /) -> None: ...


class TriObserver(Protocol[_SC, _TC, _UC]):
    def __call__(self, arg1: _SC, arg2: _TC, arg3: _UC, /) -> None: ...


class RemoveSubscriptionError(Exception):
    pass


class CallCountExceededError(RemoveSubscriptionError):
    pass


class DeadReferenceError(RemoveSubscriptionError):
    pass


class Subscription(ABC):
    def __init__(self, observer: Callable, times: int | None):
        self._positional_parameter_count = count_positional_parameters(observer)
        self.called_counter = 0
        self.max_call_count = times

    def _call(self, observer: Callable, *args) -> None:
        self.called_counter += 1
        trimmed_args = args[:self._positional_parameter_count]
        observer(*trimmed_args)
        if self.max_call_count is not None and self.called_counter >= self.max_call_count:
            raise CallCountExceededError

    @abstractmethod
    def __call__(self, *args) -> None: ...

    @abstractmethod
    def matches_observer(self, observer: Callable) -> bool: ...


class StrongSubscription(Subscription):
    def __init__(self, observer: Callable, times: int | None):
        super().__init__(observer, times)
        self._observer = observer

    def __call__(self, *args) -> None:
        self._call(self._observer, *args)

    def matches_observer(self, observer: Callable) -> bool:
        return self._observer == observer


class StrongManyToOneSubscription(Subscription):
    def __init__(self, observer: Callable, times: int | None):
        super().__init__(observer, times)
        self._observer = observer

    def __call__(self, *args_args) -> None:
        for args in args_args:
            for v in args:
                self._call(self._observer, v)

    def matches_observer(self, observer: Callable) -> bool:
        return self._observer == observer


class WeakSubscription(Subscription):
    _ref: ref[Callable] | WeakMethod

    def __init__(self, observer: Callable, times: int | None):
        super().__init__(observer, times)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    def __call__(self, *args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        self._call(observer, *args)

    def matches_observer(self, observer: Callable) -> bool:
        return self._ref() == observer


class WeakManyToOneSubscription(Subscription):
    _ref: ref[Callable] | WeakMethod

    def __init__(self, observer: Callable, times: int | None):
        super().__init__(observer, times)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    def __call__(self, *args_args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        for args in args_args:
            for v in args:
                self._call(observer, v)

    def matches_observer(self, observer: Callable) -> bool:
        return self._ref() == observer


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer, times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer, times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer) -> None: ...


class ValueObservable(Observable, Generic[_S_co], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S_co]) -> None: ...

    def derive(self, transformer: Callable[[_S_co], _T], weakly: bool = False, predicate: Callable[[_S_co], bool] | None = None) -> ValueObservable[_T]:
        return DerivedValueObservable(self, transformer, weakly=weakly, predicate=predicate)

    def derive_two(self, transformer: Callable[[_S_co], tuple[_T, _U]], weakly: bool = False, predicate: Callable[[_S_co], bool] | None = None) -> BiObservable[_T, _U]:
        return DerivedOneToTwoObservable(self, transformer, weakly=weakly, predicate=predicate)

    def derive_many(self, transformer: Callable[[_S_co], tuple[_T, ...]], weakly: bool = False, predicate: Callable[[_S_co], bool] | None = None) -> ValuesObservable[_T]:
        return DerivedOneToManyObservable(self, transformer, weakly=weakly, predicate=predicate)


class BiObservable(ValueObservable[_S], Generic[_S, _T], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                     times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None: ...


class TriObservable(BiObservable[_S, _T], Generic[_S, _T, _U], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                     times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None: ...


class ValuesObservable(Observable, Generic[_S_co], ABC):
    @abstractmethod
    def observe(self, observer: Observer | ValuesObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe(self, observer: Observer | ValuesObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def observe_single(self, observer: ValueObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def weak_observe_single(self, observer: ValueObserver[_S_co], times: int | None = None) -> None: ...

    @abstractmethod
    def unobserve(self, observer: Observer | ValuesObserver[_S_co]) -> None: ...

    def derive(self, transformer: Callable[[_S_co], _T], weakly: bool = False) -> ValuesObservable[_T]:
        return DerivedValuesObservable(self, transformer, weakly=weakly)


class _BaseObservable(Generic[_O], ABC):
    _subscriptions: list[Subscription]

    def __init__(self):
        super().__init__()
        self._subscriptions = []

    @abstractmethod
    def _get_parameter_count(self) -> int: ...

    def observe(self, observer: _O, times: int | None = None) -> None:
        assert_parameter_max_count(observer, self._get_parameter_count())
        self._subscriptions.append(StrongSubscription(observer, times))

    def weak_observe(self, observer: _O, times: int | None = None) -> None:
        assert_parameter_max_count(observer, self._get_parameter_count())
        self._subscriptions.append(WeakSubscription(observer, times))

    def unobserve(self, observer: _O) -> None:
        for i, sub in enumerate(self._subscriptions):
            if sub.matches_observer(observer):
                del self._subscriptions[i]
                return
        raise ValueError(f"Observer {observer} is not subscribed to this event.")

    def is_observed(self, by: _O | None = None) -> bool:
        if by is None:
            return len(self._subscriptions) > 0
        else:
            return any(sub.matches_observer(by) for sub in self._subscriptions)

    def _emit(self, *args) -> None:
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i](*args)
                i += 1
            except RemoveSubscriptionError:
                del self._subscriptions[i]

    def _emit_lazy(self, func: Callable[[], Sequence[Any]]) -> None:
        if len(self._subscriptions) == 0:
            return
        self._emit(*func())


class _BaseValuesObservable(_BaseObservable[_O], Generic[_O], ABC):
    def _emit_single(self, value: _S) -> None:
        self._emit((value,))

    def observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> None:
        assert_parameter_max_count(observer, 1)
        self._subscriptions.append(StrongManyToOneSubscription(observer, times))

    def weak_observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> None:
        assert_parameter_max_count(observer, 1)
        self._subscriptions.append(WeakManyToOneSubscription(observer, times))

    def _get_parameter_count(self) -> int:
        return 1

    def _emit_values(self, args: Sequence[Any]) -> None:
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i](args)
                i += 1
            except RemoveSubscriptionError:
                del self._subscriptions[i]

    def _emit_values_lazy(self, func: Callable[[], Sequence[Any]]) -> None:
        if len(self._subscriptions) == 0:
            return
        self._emit(func())


class DerivedValuesObservable(_BaseValuesObservable[Observer | ValuesObserver[_S]], ValuesObservable[_S], Generic[_S]):
    def __init__(self, derived_from: ValuesObservable[_T], transformer: Callable[[_T], _S], weakly: bool):
        super().__init__()
        self._derived_from = derived_from
        self._transformer = transformer

        def on_derived_from_change(values: Iterable[_T]) -> None:
            self._emit_values_lazy(lambda: tuple(self._transformer(v) for v in values))

        if weakly:
            self._on_derive_reference = on_derived_from_change
            self._derived_from.weak_observe(on_derived_from_change)
        else:
            derived_from.observe(on_derived_from_change)


class DerivedValueObservable(_BaseObservable[Observer | ValueObserver[_S]], ValueObservable[_S], Generic[_S]):
    def __init__(self, derived_from: ValueObservable[_T], transformer: Callable[[_T], _S], weakly: bool, predicate: Callable[[_T], bool] | None = None):
        super().__init__()
        self._derived_from = derived_from
        self._transformer = transformer
        self._predicate = predicate

        def on_derived_from_change(value: _T) -> None:
            if self._predicate is None or self._predicate(value):
                self._emit_lazy(lambda: (self._transformer(value),))

        if weakly:
            self._on_derive_reference = on_derived_from_change
            self._derived_from.weak_observe(on_derived_from_change)
        else:
            derived_from.observe(on_derived_from_change)

    def _get_parameter_count(self) -> int:
        return 1


class DerivedOneToTwoObservable(_BaseObservable[Observer | ValueObserver[_S] | BiObserver[_S, _T]], BiObservable[_S, _T], Generic[_S, _T]):
    def __init__(self, derived_from: ValueObservable[_U], transformer: Callable[[_U], tuple[_S, _T]], weakly: bool, predicate: Callable[[_U], bool] | None = None):
        super().__init__()
        self._derived_from = derived_from
        self._transformer = transformer
        self._predicate = predicate

        def on_derived_from_change(value: _U) -> None:
            if self._predicate is None or self._predicate(value):
                self._emit_lazy(lambda: self._transformer(value))

        if weakly:
            self._on_derive_reference = on_derived_from_change
            self._derived_from.weak_observe(on_derived_from_change)
        else:
            derived_from.observe(on_derived_from_change)

    def _get_parameter_count(self) -> int:
        return 2


class DerivedOneToManyObservable(_BaseValuesObservable[Observer | ValuesObserver[_S]], ValuesObservable[_S], Generic[_S]):
    def __init__(self, derived_from: ValueObservable[_U], transformer: Callable[[_U], tuple[_S, ...]], weakly: bool, predicate: Callable[[_U], bool] | None = None):
        super().__init__()
        self._derived_from = derived_from
        self._transformer = transformer
        self._predicate = predicate

        def on_derived_from_change(value: _U) -> None:
            if self._predicate is None or self._predicate(value):
                self._emit_values_lazy(lambda: self._transformer(value))

        if weakly:
            self._on_derive_reference = on_derived_from_change
            self._derived_from.weak_observe(on_derived_from_change)
        else:
            derived_from.observe(on_derived_from_change)

    def _get_parameter_count(self) -> int:
        return 1


class _VoidObservable(Observable):
    def observe(self, observer: Observer, times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe(self, observer: Observer, times: int | None = None) -> None:
        pass  # pragma: no cover

    def unobserve(self, observer: Observer) -> None:
        pass  # pragma: no cover


class _VoidValueObservable(ValueObservable[_S], Generic[_S]):
    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        pass  # pragma: no cover


class _VoidBiObservable(BiObservable[_S, _T], Generic[_S, _T]):
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                     times: int | None = None) -> None:
        pass  # pragma: no cover

    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        pass  # pragma: no cover


class _VoidTriObservable(TriObservable[_S, _T, _U], Generic[_S, _T, _U]):
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                     times: int | None = None) -> None:
        pass  # pragma: no cover

    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        pass  # pragma: no cover


class _VoidValuesObservable(ValuesObservable[_S], Generic[_S]):
    def observe(self, observer: Observer | ValuesObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe(self, observer: Observer | ValuesObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def weak_observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> None:
        pass  # pragma: no cover

    def unobserve(self, observer: Observer | ValuesObserver[_S]) -> None:
        pass  # pragma: no cover


VOID_OBSERVABLE: Observable = _VoidObservable()
VOID_VALUE_OBSERVABLE: ValueObservable = _VoidValueObservable()
VOID_BI_OBSERVABLE: BiObservable = _VoidBiObservable()
VOID_TRI_OBSERVABLE: TriObservable = _VoidTriObservable()
VOID_VALUES_OBSERVABLE: ValuesObservable = _VoidValuesObservable()


def void_observable() -> Observable:
    return VOID_OBSERVABLE


def void_value_observable() -> ValueObservable[_S]:
    return VOID_VALUE_OBSERVABLE


def void_bi_observable() -> BiObservable[_S, _T]:
    return VOID_BI_OBSERVABLE


def void_tri_observable() -> TriObservable[_S, _T, _U]:
    return VOID_TRI_OBSERVABLE


def void_values_observable() -> ValuesObservable[_S]:
    return VOID_VALUES_OBSERVABLE
