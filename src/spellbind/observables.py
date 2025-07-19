from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, Protocol, Iterable, Any, Sequence
from weakref import WeakMethod, ref

from typing_extensions import override

from spellbind.functions import count_positional_parameters, assert_parameter_max_count, has_var_args

_S_contra = TypeVar("_S_contra", contravariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)
_U_contra = TypeVar("_U_contra", contravariant=True)
_I_contra = TypeVar("_I_contra", bound=Iterable, contravariant=True)

_S_co = TypeVar("_S_co", covariant=True)
_T_co = TypeVar("_T_co", covariant=True)
_U_co = TypeVar("_U_co", covariant=True)

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_W = TypeVar("_W")
_I = TypeVar("_I", bound=Iterable)


_O = TypeVar('_O', bound=Callable)


class Observer(Protocol):
    def __call__(self) -> None: ...


class ValueObserver(Protocol[_S_contra]):
    def __call__(self, arg: _S_contra, /) -> None: ...


class ValuesObserver(Protocol[_S_contra]):
    def __call__(self, args: Iterable[_S_contra], /) -> None: ...


class BiObserver(Protocol[_S_contra, _T_contra]):
    def __call__(self, arg1: _S_contra, arg2: _T_contra, /) -> None: ...


class TriObserver(Protocol[_S_contra, _T_contra, _U_contra]):
    def __call__(self, arg1: _S_contra, arg2: _T_contra, arg3: _U_contra, /) -> None: ...


class RemoveSubscriptionError(Exception):
    pass


class CallCountExceededError(RemoveSubscriptionError):
    pass


class DeadReferenceError(RemoveSubscriptionError):
    pass


class Subscription(ABC):
    def __init__(self, observer: Callable, times: int | None, on_silent_change: Callable[[bool], None]):
        self._positional_parameter_count = -1
        if not has_var_args(observer):
            self._positional_parameter_count = count_positional_parameters(observer)
        self._call_counter = 0
        self._max_call_count = times
        self._silent = False
        self._on_silent_change = on_silent_change

    def _call(self, observer: Callable, *args) -> None:
        if not self._silent:
            self._call_counter += 1
            if self._positional_parameter_count == -1:
                trimmed_args = args
            else:
                trimmed_args = args[:self._positional_parameter_count]
            observer(*trimmed_args)
            if self._max_call_count is not None and self._call_counter >= self._max_call_count:
                raise CallCountExceededError

    @property
    def call_counter(self) -> int:
        return self._call_counter

    @property
    def max_call_count(self) -> int | None:
        return self._max_call_count

    @property
    def silent(self) -> bool:
        return self._silent

    @silent.setter
    def silent(self, value: bool) -> None:
        if self._silent != value:
            self._silent = value
            self._on_silent_change(value)

    @abstractmethod
    def __call__(self, *args) -> None: ...

    @abstractmethod
    def matches_observer(self, observer: Callable) -> bool: ...


class StrongSubscription(Subscription):
    def __init__(self, observer: Callable, times: int | None, on_silent_change: Callable[[bool], None]):
        super().__init__(observer, times, on_silent_change)
        self._observer = observer

    @override
    def __call__(self, *args) -> None:
        self._call(self._observer, *args)

    @override
    def matches_observer(self, observer: Callable) -> bool:
        return self._observer == observer


class StrongManyToOneSubscription(Subscription):
    def __init__(self, observer: Callable, times: int | None, on_silent_change: Callable[[bool], None]):
        super().__init__(observer, times, on_silent_change)
        self._observer = observer

    @override
    def __call__(self, *args_args) -> None:
        for args in args_args:
            for v in args:
                self._call(self._observer, v)

    @override
    def matches_observer(self, observer: Callable) -> bool:
        return self._observer == observer


class WeakSubscription(Subscription):
    _ref: ref[Callable] | WeakMethod

    def __init__(self, observer: Callable, times: int | None, on_silent_change: Callable[[bool], None]):
        super().__init__(observer, times, on_silent_change)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    @override
    def __call__(self, *args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        self._call(observer, *args)

    @override
    def matches_observer(self, observer: Callable) -> bool:
        return self._ref() == observer


class WeakManyToOneSubscription(Subscription):
    _ref: ref[Callable] | WeakMethod

    def __init__(self, observer: Callable, times: int | None, on_silent_change: Callable[[bool], None]):
        super().__init__(observer, times, on_silent_change)
        if hasattr(observer, '__self__'):
            self._ref = WeakMethod(observer)
        else:
            self._ref = ref(observer)

    @override
    def __call__(self, *args_args) -> None:
        observer = self._ref()
        if observer is None:
            raise DeadReferenceError()
        for args in args_args:
            for v in args:
                self._call(observer, v)

    @override
    def matches_observer(self, observer: Callable) -> bool:
        return self._ref() == observer


class Observable(ABC):
    @abstractmethod
    def observe(self, observer: Observer, times: int | None = None) -> Subscription: ...

    @abstractmethod
    def weak_observe(self, observer: Observer, times: int | None = None) -> Subscription: ...

    @abstractmethod
    def unobserve(self, observer: Observer) -> None: ...

    @abstractmethod
    def is_observed(self, by: _O | None = None) -> bool: ...

    def __or__(self, other: Observable) -> Observable:
        return CombinedObservable((self, other), weakly=True)


class ValueObservable(Observable, Generic[_S_co], ABC):
    @abstractmethod
    @override
    def observe(self, observer: Observer | ValueObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def unobserve(self, observer: Observer | ValueObserver[_S_co]) -> None: ...

    def map(self, transformer: Callable[[_S_co], _T], weakly: bool = False,
            predicate: Callable[[_S_co], bool] | None = None) -> ValueObservable[_T]:
        return MappedValueObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_two(self, transformer: Callable[[_S_co], tuple[_T, _U]], weakly: bool = False,
                   predicate: Callable[[_S_co], bool] | None = None) -> BiObservable[_T, _U]:
        return SplitOneInTwoObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_three(self, transformer: Callable[[_S_co], tuple[_T, _U, _V]], weakly: bool = False,
                     predicate: Callable[[_S_co], bool] | None = None) -> TriObservable[_T, _U, _V]:
        return SplitOneInThreeObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_many(self, transformer: Callable[[_S_co], tuple[_T, ...]], weakly: bool = False,
                    predicate: Callable[[_S_co], bool] | None = None) -> ValuesObservable[_T]:
        return SplitOneInManyObservable(self, transformer, weakly=weakly, predicate=predicate)

    def or_value(self, other: ValueObservable[_T]) -> ValueObservable[_S_co | _T]:
        return CombinedValueObservable((self, other), weakly=True)


class BiObservable(Observable, Generic[_S_co, _T_co], ABC):
    @abstractmethod
    @override
    def observe(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co],
                times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co],
                     times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def unobserve(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co]) -> None: ...

    def map_to_one(self, transformer: Callable[[_S_co, _T_co], _U], weakly: bool = False,
                   predicate: Callable[[_S_co, _T_co], bool] | None = None) -> ValueObservable[_U]:
        return MergeTwoToOneObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map(self, transformer: Callable[[_S_co, _T_co], tuple[_U, _V]], weakly: bool = False,
            predicate: Callable[[_S_co, _T_co], bool] | None = None) -> BiObservable[_U, _V]:
        return MappedBiObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_three(self, transformer: Callable[[_S_co, _T_co], tuple[_U, _V, _W]], weakly: bool = False,
                     predicate: Callable[[_S_co, _T_co], bool] | None = None) -> TriObservable[_U, _V, _W]:
        return SplitTwoToThreeObservable(self, transformer, weakly=weakly, predicate=predicate)

    def or_bi(self, other: BiObservable[_S_co, _T_co]) -> BiObservable[_S_co, _T_co]:
        return CombinedBiObservable((self, other), weakly=True)


class TriObservable(BiObservable[_S_co, _T_co], Generic[_S_co, _T_co, _U_co], ABC):
    @abstractmethod
    @override
    def observe(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co] | TriObserver[_S_co, _T_co, _U_co],
                times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co] | TriObserver[_S_co, _T_co, _U_co],
                     times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def unobserve(self, observer: Observer | ValueObserver[_S_co] | BiObserver[_S_co, _T_co] | TriObserver[_S_co, _T_co, _U_co]) -> None: ...

    def or_tri(self, other: TriObservable[_S_co, _T_co, _U_co]) -> TriObservable[_S_co, _T_co, _U_co]:
        return CombinedTriObservable((self, other), weakly=True)


class ValuesObservable(Observable, Generic[_S_co], ABC):
    @abstractmethod
    @override
    def observe(self, observer: Observer | ValuesObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def weak_observe(self, observer: Observer | ValuesObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    def observe_single(self, observer: ValueObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    def weak_observe_single(self, observer: ValueObserver[_S_co], times: int | None = None) -> Subscription: ...

    @abstractmethod
    @override
    def unobserve(self, observer: Observer | ValuesObserver[_S_co]) -> None: ...

    def map_to_one(self, transformer: Callable[[Iterable[_S_co]], _T_co], weakly: bool = False,
                   predicate: Callable[[Iterable[_S_co]], bool] | None = None) -> ValueObservable[_T_co]:
        return MergedValuesObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_two(self, transformer: Callable[[Iterable[_S_co]], tuple[_T_co, _U_co]], weakly: bool = False,
                   predicate: Callable[[Iterable[_S_co]], bool] | None = None) -> BiObservable[_T_co, _U_co]:
        return MergeManyToTwoObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map_to_three(self, transformer: Callable[[Iterable[_S_co]], tuple[_T_co, _U_co, _V]], weakly: bool = False,
                     predicate: Callable[[Iterable[_S_co]], bool] | None = None) -> TriObservable[_T_co, _U_co, _V]:
        return MergeManyToThreeObservable(self, transformer, weakly=weakly, predicate=predicate)

    def map(self, transformer: Callable[[_S_co], _T_co], weakly: bool = False,
            predicate: Callable[[_S_co], bool] | None = None) -> ValuesObservable[_T_co]:
        return MappedValuesObservable(self, transformer, weakly=weakly, predicate=predicate)

    def or_values(self, other: ValuesObservable[_T]) -> ValuesObservable[_S_co | _T]:
        return CombinedValuesObservable((self, other), weakly=True)


class _BaseObservable(Generic[_O], ABC):
    _subscriptions: list[Subscription]

    def __init__(self):
        super().__init__()
        self._subscriptions = []
        self._active_subscription_count = 0

    def _on_subscription_silent_change(self, silent: bool) -> None:
        if silent:
            self._active_subscription_count -= 1
        else:
            self._active_subscription_count += 1

    @abstractmethod
    def _get_parameter_count(self) -> int: ...

    def observe(self, observer: _O, times: int | None = None) -> Subscription:
        assert_parameter_max_count(observer, self._get_parameter_count())
        subscription = StrongSubscription(observer, times, on_silent_change=self._on_subscription_silent_change)
        self._append_subscription(subscription)
        return subscription

    def weak_observe(self, observer: _O, times: int | None = None) -> Subscription:
        assert_parameter_max_count(observer, self._get_parameter_count())
        subscription = WeakSubscription(observer, times, on_silent_change=self._on_subscription_silent_change)
        self._append_subscription(subscription)
        return subscription

    def _append_subscription(self, subscription: Subscription):
        self._subscriptions.append(subscription)
        if not subscription.silent:
            self._active_subscription_count += 1

    def _del_subscription(self, index: int):
        sub = self._subscriptions.pop(index)
        if not sub.silent:
            self._active_subscription_count -= 1

    def unobserve(self, observer: _O) -> None:
        for i, sub in enumerate(self._subscriptions):
            if sub.matches_observer(observer):
                self._del_subscription(i)
                return
        raise ValueError(f"Observer {observer} is not subscribed to this event.")

    def is_observed(self, by: _O | None = None) -> bool:
        if by is None:
            return self._active_subscription_count > 0
        else:
            return any(sub.matches_observer(by) for sub in self._subscriptions)

    def _emit_n(self, args: Sequence[Any]) -> None:
        if not self.is_observed():
            return
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i](*args)
                i += 1
            except RemoveSubscriptionError:
                self._del_subscription(i)

    def _emit_nothing(self) -> None:
        if not self.is_observed():
            return
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i]()
                i += 1
            except RemoveSubscriptionError:
                self._del_subscription(i)

    def _emit_n_lazy(self, func: Callable[[], Sequence[Any]]) -> None:
        if not self.is_observed():
            return
        self._emit_n(func())


class _SingleBaseObservable(_BaseObservable[_O], Generic[_O], ABC):
    def _emit_single(self, arg: Any) -> None:
        if not self.is_observed():
            return
        i = 0
        while i < len(self._subscriptions):
            try:
                self._subscriptions[i](arg)
                i += 1
            except RemoveSubscriptionError:
                self._del_subscription(i)

    def _emit_single_lazy(self, func: Callable[[], Any]) -> None:
        if not self.is_observed():
            return
        value = func()
        self._emit_single(value)

    @override
    def _get_parameter_count(self) -> int:
        return 1


class _DerivedObservableBase(_BaseObservable[_O], Generic[_O], ABC):
    def __init__(self, weakly: bool, transformer: Callable | None, predicate: Callable | None):
        super().__init__()
        if transformer is None:

            def transformer(*args: Any) -> Any:
                return args
        self._transformer = transformer
        self._predicate = predicate
        self._weakly = weakly

    @override
    def _append_subscription(self, subscription: Subscription):
        super()._append_subscription(subscription)
        self._set_subscriptions_silent(False)

    @override
    def _del_subscription(self, index: int):
        super()._del_subscription(index)
        if not self.is_observed():
            self._set_subscriptions_silent(True)

    @override
    def _on_subscription_silent_change(self, silent: bool) -> None:
        super()._on_subscription_silent_change(silent)
        if silent:
            if not self.is_observed():
                self._set_subscriptions_silent(True)
        else:
            self._set_subscriptions_silent(False)

    def _on_derived_emit(self, *values) -> None:
        if self._predicate is None or self._predicate(*values):
            self._emit_n_lazy(lambda: self._transformer(*values))

    @abstractmethod
    def _set_subscriptions_silent(self, silent: bool): ...


class _DerivedFromOneObservableBase(_DerivedObservableBase[_O], Generic[_O], ABC):
    def __init__(self, derived_from: Observable, transformer: Callable, weakly: bool, predicate: Callable | None):
        super().__init__(weakly, transformer, predicate)
        self._derived_from = derived_from

        if self._weakly:
            self._derived_from_subscription = derived_from.weak_observe(self._on_derived_emit)
        else:
            self._derived_from_subscription = derived_from.observe(self._on_derived_emit)
        self._set_subscriptions_silent(True)

    @override
    def _set_subscriptions_silent(self, silent: bool):
        self._derived_from_subscription.silent = silent


class _DerivedFromManyObservableBase(_DerivedObservableBase[_O], Generic[_O], ABC):
    def __init__(self, derived_from: Iterable[Observable], weakly: bool, transformer: Callable | None, predicate: Callable | None):
        super().__init__(weakly, transformer=transformer, predicate=predicate)
        self._derived_from = derived_from
        if self._weakly:
            self._derived_from_subscriptions = tuple(d.weak_observe(self._on_derived_emit) for d in derived_from)
        else:
            self._derived_from_subscriptions = tuple(d.observe(self._on_derived_emit) for d in derived_from)
        self._set_subscriptions_silent(True)

    @override
    def _set_subscriptions_silent(self, silent: bool):
        for sub in self._derived_from_subscriptions:
            sub.silent = silent


class _BaseValuesObservable(_SingleBaseObservable[_O], Generic[_O], ABC):
    def observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> Subscription:
        assert_parameter_max_count(observer, 1)
        subscription = StrongManyToOneSubscription(observer, times, self._on_subscription_silent_change)
        self._append_subscription(subscription)
        return subscription

    def weak_observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> Subscription:
        assert_parameter_max_count(observer, 1)
        subscription = WeakManyToOneSubscription(observer, times, self._on_subscription_silent_change)
        self._append_subscription(subscription)
        return subscription


class CombinedObservable(_DerivedFromManyObservableBase[Observer], Observable):
    def __init__(self, derived_from: Iterable[Observable], weakly: bool = False):
        super().__init__(derived_from=derived_from, weakly=weakly, transformer=None, predicate=None)

    @override
    def _get_parameter_count(self) -> int:
        return 0


class CombinedValueObservable(_DerivedFromManyObservableBase[Observer | ValueObserver[_S]],
                              ValueObservable[_S],
                              Generic[_S]):
    def __init__(self, derived_from: Iterable[ValueObservable[_S]], weakly: bool = False):
        super().__init__(derived_from=derived_from, weakly=weakly, transformer=None, predicate=None)

    @override
    def _get_parameter_count(self) -> int:
        return 1


class CombinedBiObservable(_DerivedFromManyObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T]],
                           BiObservable[_S, _T],
                           Generic[_S, _T]):
    def __init__(self, derived_from: Iterable[BiObservable[_S, _T]], weakly: bool = False):
        super().__init__(derived_from=derived_from, weakly=weakly, transformer=None, predicate=None)

    @override
    def _get_parameter_count(self) -> int:
        return 2


class CombinedTriObservable(_DerivedFromManyObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]],
                            TriObservable[_S, _T, _U],
                            Generic[_S, _T, _U]):
    def __init__(self, derived_from: Iterable[TriObservable[_S, _T, _U]], weakly: bool = False):
        super().__init__(derived_from=derived_from, weakly=weakly, transformer=None, predicate=None)

    @override
    def _get_parameter_count(self) -> int:
        return 3


class CombinedValuesObservable(_DerivedFromManyObservableBase[Observer | ValuesObserver[_S]],
                               _BaseValuesObservable[Observer | ValuesObserver[_S]],
                               ValuesObservable[_S],
                               Generic[_S]):
    def __init__(self, derived_from: Iterable[ValuesObservable[_S]], weakly: bool = False):
        super().__init__(derived_from=derived_from, weakly=weakly, transformer=None, predicate=None)

    @override
    def _get_parameter_count(self) -> int:
        return 1


class MergedValuesObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S]],
                             _SingleBaseObservable[Observer | ValueObserver[_S]],
                             ValueObservable[_S],
                             Generic[_S]):
    def __init__(self,
                 derived_from: ValuesObservable[_T],
                 transformer: Callable[[Iterable[_T]], _S],
                 weakly: bool,
                 predicate: Callable[[Iterable[_T]], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, values: Iterable[_T]) -> None:
        if self._predicate is None or self._predicate(values):
            self._emit_single_lazy(lambda: self._transformer(values))


class MergeManyToTwoObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T]],
                               BiObservable[_S, _T],
                               Generic[_S, _T]):

    def __init__(self,
                 derived_from: ValuesObservable[_U],
                 transformer: Callable[[Iterable[_U]], tuple[_S, _T]],
                 weakly: bool,
                 predicate: Callable[[Iterable[_U]], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, values: Iterable[_U]) -> None:
        if self._predicate is None or self._predicate(values):
            self._emit_n_lazy(lambda: self._transformer(values))

    @override
    def _get_parameter_count(self) -> int:
        return 2


class MergeManyToThreeObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]],
                                 TriObservable[_S, _T, _U],
                                 Generic[_S, _T, _U]):
    def __init__(self,
                 derived_from: ValuesObservable[_V],
                 transformer: Callable[[Iterable[_V]], tuple[_S, _T, _U]],
                 weakly: bool,
                 predicate: Callable[[Iterable[_V]], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, values: Iterable[_V]) -> None:
        if self._predicate is None or self._predicate(values):
            self._emit_n_lazy(lambda: self._transformer(values))

    @override
    def _get_parameter_count(self) -> int:
        return 3


class MappedValuesObservable(_DerivedFromOneObservableBase[Observer | ValuesObserver[_S]],
                             _BaseValuesObservable[Observer | ValuesObserver[_S]],
                             ValuesObservable[_S],
                             Generic[_S]):
    def __init__(self,
                 derived_from: ValuesObservable[_T],
                 transformer: Callable[[_T], _S],
                 weakly: bool,
                 predicate: Callable[[_T], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, values) -> None:
        predicate = self._predicate
        if predicate is None:
            self._emit_single_lazy(lambda: tuple(self._transformer(value) for value in values))
        else:
            self._emit_single_lazy(lambda: tuple(self._transformer(value) for value in values if predicate(value)))


class MappedValueObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S]],
                            _SingleBaseObservable[Observer | ValueObserver[_S]],
                            ValueObservable[_S],
                            Generic[_S]):
    def __init__(self,
                 derived_from: ValueObservable[_T],
                 transformer: Callable[[_T], _S],
                 weakly: bool,
                 predicate: Callable[[_T], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _get_parameter_count(self) -> int:
        return 1

    @override
    def _on_derived_emit(self, value) -> None:
        if self._predicate is None or self._predicate(value):
            self._emit_single_lazy(lambda: self._transformer(value))


class SplitOneInTwoObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T]],
                              BiObservable[_S, _T],
                              Generic[_S, _T]):
    def __init__(self,
                 derived_from: ValueObservable[_U],
                 transformer: Callable[[_U], tuple[_S, _T]],
                 weakly: bool,
                 predicate: Callable[[_U], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _get_parameter_count(self) -> int:
        return 2


class SplitOneInThreeObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]],
                                TriObservable[_S, _T, _U],
                                Generic[_S, _T, _U]):
    def __init__(self,
                 derived_from: ValueObservable[_V],
                 transformer: Callable[[_V], tuple[_S, _T, _U]],
                 weakly: bool,
                 predicate: Callable[[_V], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _get_parameter_count(self) -> int:
        return 3


class SplitOneInManyObservable(_DerivedFromOneObservableBase[Observer | ValuesObserver[_S]],
                               _BaseValuesObservable[Observer | ValuesObserver[_S]],
                               ValuesObservable[_S],
                               Generic[_S]):
    def __init__(self,
                 derived_from: ValueObservable[_T],
                 transformer: Callable[[_T], tuple[_S, ...]],
                 weakly: bool,
                 predicate: Callable[[_T], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, value) -> None:
        predicate = self._predicate
        if predicate is None or predicate(value):
            self._emit_single_lazy(lambda: self._transformer(value))


class MergeTwoToOneObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S]],
                              _SingleBaseObservable[Observer | ValueObserver[_S]],
                              ValueObservable[_S],
                              Generic[_S]):
    def __init__(self,
                 derived_from: BiObservable[_T, _U],
                 transformer: Callable[[_T, _U], _S],
                 weakly: bool,
                 predicate: Callable[[_T, _U], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _on_derived_emit(self, value_0: _T, value_1: _U) -> None:
        if self._predicate is None or self._predicate(value_0, value_1):
            self._emit_single_lazy(lambda: self._transformer(value_0, value_1))


class MappedBiObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T]],
                         BiObservable[_S, _T],
                         Generic[_S, _T]):
    def __init__(self,
                 derived_from: BiObservable[_U, _V],
                 transformer: Callable[[_U, _V], tuple[_S, _T]],
                 weakly: bool,
                 predicate: Callable[[_U, _V], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _get_parameter_count(self) -> int:
        return 2


class SplitTwoToThreeObservable(_DerivedFromOneObservableBase[Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]],
                                TriObservable[_S, _T, _U],
                                Generic[_S, _T, _U]):
    def __init__(self,
                 derived_from: BiObservable[_V, _W],
                 transformer: Callable[[_V, _W], tuple[_S, _T, _U]],
                 weakly: bool,
                 predicate: Callable[[_V, _W], bool] | None = None):
        super().__init__(derived_from, transformer, weakly, predicate)

    @override
    def _get_parameter_count(self) -> int:
        return 3


class _VoidSubscription(Subscription):
    def __init__(self):
        super().__init__(lambda: None, None, lambda silent: None)

    @override
    def __call__(self, *args) -> None:
        pass  # pragma: no cover

    @override
    def matches_observer(self, observer: Callable) -> bool:
        return False  # pragma: no cover


VOID_SUBSCRIPTION = _VoidSubscription()


class _VoidObservable(Observable):
    @override
    def observe(self, observer: Observer, times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe(self, observer: Observer, times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def unobserve(self, observer: Observer) -> None:
        pass  # pragma: no cover

    @override
    def is_observed(self, by: Observer | None = None) -> bool:
        return False  # pragma: no cover


class _VoidValueObservable(ValueObservable[_S], Generic[_S]):
    @override
    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        pass  # pragma: no cover

    @override
    def is_observed(self, by: Observer | ValueObserver[_S] | None = None) -> bool:
        return False  # pragma: no cover


class _VoidBiObservable(BiObservable[_S, _T], Generic[_S, _T]):
    @override
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T],
                     times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T]) -> None:
        pass  # pragma: no cover

    @override
    def is_observed(self, by: Observer | ValueObserver[_S] | BiObserver[_S, _T] | None = None) -> bool:
        return False  # pragma: no cover


class _VoidTriObservable(TriObservable[_S, _T, _U], Generic[_S, _T, _U]):
    @override
    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U],
                     times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U]) -> None:
        pass  # pragma: no cover

    @override
    def is_observed(self, by: Observer | ValueObserver[_S] | BiObserver[_S, _T] | TriObserver[_S, _T, _U] | None = None) -> bool:
        return False  # pragma: no cover


class _VoidValuesObservable(ValuesObservable[_S], Generic[_S]):
    @override
    def observe(self, observer: Observer | ValuesObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe(self, observer: Observer | ValuesObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def weak_observe_single(self, observer: ValueObserver[_S], times: int | None = None) -> Subscription:
        return VOID_SUBSCRIPTION  # pragma: no cover

    @override
    def unobserve(self, observer: Observer | ValuesObserver[_S]) -> None:
        pass  # pragma: no cover

    @override
    def is_observed(self, by: Observer | ValuesObserver[_S] | None = None) -> bool:
        return False  # pragma: no cover


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
