from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any, Iterable, TYPE_CHECKING, Callable

from spellbind.event import ValueEvent
from spellbind.observables import ValueObservable, Observer, ValueObserver

if TYPE_CHECKING:
    from spellbind.str_values import StrValue
    from spellbind.int_values import IntValue
    from spellbind.bool_values import BoolValue


EMPTY_FROZEN_SET: frozenset = frozenset()

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


class Value(ValueObservable[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def value(self) -> _S:
        raise NotImplementedError

    @abstractmethod
    def derived_from(self) -> frozenset[Value]:
        raise NotImplementedError

    @property
    def deep_derived_from(self) -> Iterable[Value]:
        found_derived = set()
        derive_queue = [self]

        while derive_queue:
            current = derive_queue.pop(0)
            for dependency in current.derived_from():
                if dependency not in found_derived:
                    found_derived.add(dependency)
                    yield dependency
                    derive_queue.append(dependency)

    def is_dependent_on(self, value: Value[Any]) -> bool:
        for dependency in self.deep_derived_from:
            if value is dependency:
                return True
        return False

    def to_str(self) -> StrValue:
        from spellbind.str_values import ToStrValue
        return ToStrValue(self)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def map(self, transformer: Callable[[_S], _T]) -> Value[_T]:
        return MappedValue(self, transformer)

    def map_to_int(self, transformer: Callable[[_S], int]) -> IntValue:
        from spellbind.int_values import MappedIntValue
        return MappedIntValue(self, transformer)

    def map_to_float(self, transformer: Callable[[_S], float]) -> Value[float]:
        from spellbind.float_values import MappedFloatValue
        return MappedFloatValue(self, transformer)

    def map_to_str(self, transformer: Callable[[_S], str]) -> StrValue:
        from spellbind.str_values import MappedStrValue
        return MappedStrValue(self, transformer)

    def map_to_bool(self, transformer: Callable[[_S], bool]) -> BoolValue:
        from spellbind.bool_values import MappedBoolValue
        return MappedBoolValue(self, transformer)


class Variable(Value[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def value(self) -> _S:
        raise NotImplementedError

    @value.setter
    @abstractmethod
    def value(self, new_value: _S) -> None:
        raise NotImplementedError

    @abstractmethod
    def bind_to(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None:
        raise NotImplementedError

    @abstractmethod
    def unbind(self, not_bound_ok: bool = False) -> None:
        raise NotImplementedError


class SimpleVariable(Variable[_S], Generic[_S]):
    _bound_to_set: frozenset[Value[_S]]
    _on_change: ValueEvent[_S]
    _bound_to: Optional[Value[_S]]

    def __init__(self, value: _S):
        self._bound_to_set = EMPTY_FROZEN_SET
        self._value = value
        self._on_change = ValueEvent()
        self._bound_to = None

    @property
    def value(self) -> _S:
        return self._value

    @value.setter
    def value(self, new_value: _S) -> None:
        if self._bound_to is not None:
            raise ValueError("Cannot set value of a Variable that is bound to a Value.")
        self._set_value_bypass_bound_check(new_value)

    def _set_value_bypass_bound_check(self, new_value: _S) -> None:
        if new_value != self._value:
            self._value = new_value
            self._on_change(new_value)

    def _receive_bound_value(self, value: _S) -> None:
        self._set_value_bypass_bound_check(value)

    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.observe(observer, times)

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        self._on_change.weak_observe(observer, times)

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        self._on_change.unobserve(observer)

    def bind_to(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None:
        if value is self:
            raise RecursionError("Cannot bind a Variable to itself.")
        if value.is_dependent_on(self):
            raise RecursionError("Circular binding detected.")
        if self._bound_to is not None:
            if not already_bound_ok:
                raise ValueError("Variable is already bound to another Value.")
            if self._bound_to is value:
                return
            self.unbind()
        if bind_weakly:
            value.weak_observe(self._receive_bound_value)
        else:
            value.observe(self._receive_bound_value)
        self._bound_to = value
        self._bound_to_set = frozenset([value])
        self._set_value_bypass_bound_check(value.value)

    def unbind(self, not_bound_ok: bool = False) -> None:
        if self._bound_to is None:
            if not not_bound_ok:
                raise ValueError("Variable is not bound to any Value.")
            else:
                return

        self._bound_to.unobserve(self._receive_bound_value)
        self._bound_to = None
        self._bound_to_set = EMPTY_FROZEN_SET

    def derived_from(self) -> frozenset[Value[_S]]:
        return self._bound_to_set


class Constant(Value[_S], Generic[_S]):
    _value: _S

    def __init__(self, value: _S):
        self._value = value

    @property
    def value(self) -> _S:
        return self._value

    def observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass

    def weak_observe(self, observer: Observer | ValueObserver[_S], times: int | None = None) -> None:
        pass

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        pass

    def derived_from(self) -> frozenset[Value[_S]]:
        return EMPTY_FROZEN_SET


class DerivedValueBase(Value[_T], Generic[_T], ABC):
    def __init__(self, *values: Value):
        self._values = frozenset(values)
        self._on_change: ValueEvent[_T] = ValueEvent()

    def derived_from(self) -> frozenset[Value]:
        return self._values

    def observe(self, observer: Observer | ValueObserver[_T], times: int | None = None) -> None:
        self._on_change.observe(observer, times)

    def weak_observe(self, observer: Observer | ValueObserver[_T], times: int | None = None) -> None:
        self._on_change.weak_observe(observer, times)

    def unobserve(self, observer: Observer | ValueObserver[_T]) -> None:
        self._on_change.unobserve(observer)


class DerivedValue(DerivedValueBase[_T], Generic[_S, _T], ABC):
    def __init__(self, of: Value[_S]):
        super().__init__(of)
        self._value = self.transform(of.value)
        of.weak_observe(self._on_source_change)

    @abstractmethod
    def transform(self, value: _S) -> _T:
        raise NotImplementedError

    def _on_source_change(self, new_source_value: _S) -> None:
        new_transformed_value = self.transform(new_source_value)
        if new_transformed_value != self._value:
            self._value = new_transformed_value
            self._on_change(self._value)

    @property
    def value(self) -> _T:
        return self._value


class MappedValue(DerivedValue[_S, _T], Generic[_S, _T]):
    def __init__(self, of: Value[_S], transformer: Callable[[_S], _T]):
        super().__init__(of)
        self._transformer = transformer
        self._of = of

    def transform(self, value: _S) -> _T:
        return self._transformer(value)


def _create_value_getter(value: Value[_S] | _S) -> Callable[[], _S]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


class CombinedTwoValues(DerivedValueBase[_U], Generic[_S, _T, _U], ABC):
    _on_change: ValueEvent[_U]

    def __init__(self, left: Value[_S] | _S, right: Value[_T] | _T):
        super().__init__(*[v for v in (left, right) if isinstance(v, Value)])
        self._left_getter = _create_value_getter(left)
        self._right_getter = _create_value_getter(right)
        if isinstance(left, Value):
            left.weak_observe(self._on_left_change)
        if isinstance(right, Value):
            right.weak_observe(self._on_right_change)
        self._value = self.transform(self._left_getter(), self._right_getter())

    def _on_left_change(self, new_left_value: _S) -> None:
        new_value = self.transform(new_left_value, self._right_getter())
        self._on_result_change(new_value)

    def _on_right_change(self, new_right_value: _T) -> None:
        new_value = self.transform(self._left_getter(), new_right_value)
        self._on_result_change(new_value)

    def _on_result_change(self, new_value: _U) -> None:
        if new_value != self._value:
            self._value = new_value
            self._on_change(self._value)

    @abstractmethod
    def transform(self, left: _S, right: _T) -> _U:
        raise NotImplementedError

    @property
    def value(self) -> _U:
        return self._value


def _get_value(value: Value[_S] | _S) -> _S:
    if isinstance(value, Value):
        return value.value
    else:
        return value


class CombinedMixedValues(DerivedValueBase[_T], Generic[_S, _T], ABC):
    def __init__(self, *sources: Value[_S] | _S):
        super().__init__(*[v for v in sources if isinstance(v, Value)])
        self.gotten_values = [_get_value(v) for v in sources]
        self._callbacks: list[Callable] = []
        for i, v in enumerate(sources):
            if isinstance(v, Value):
                v.weak_observe(self._create_on_n_changed(i))
        self._value = self._calculate_value()

    def _create_on_n_changed(self, index: int) -> Callable[[_S], None]:
        def on_change(new_value: _S) -> None:
            self.gotten_values[index] = new_value
            self._on_result_change(self._calculate_value())
        self._callbacks.append(on_change)  # keep strong reference to callback so it won't be garbage collected
        return on_change

    def _calculate_value(self) -> _T:
        return self.transform(*self.gotten_values)

    def _on_result_change(self, new_value: _T) -> None:
        if new_value != self._value:
            self._value = new_value
            self._on_change(self._value)

    @abstractmethod
    def transform(self, *args: _S) -> _T:
        raise NotImplementedError

    @property
    def value(self) -> _T:
        return self._value
