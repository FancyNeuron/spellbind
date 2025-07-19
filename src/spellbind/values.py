from __future__ import annotations

from typing_extensions import deprecated, override

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TypeVar, Generic, Optional, Iterable, TYPE_CHECKING, Callable, Sequence, ContextManager, \
    Generator

from spellbind.deriveds import Derived
from spellbind.event import BiEvent
from spellbind.observables import Observer, ValueObserver, BiObservable, BiObserver, Subscription, void_bi_observable

if TYPE_CHECKING:
    from spellbind.str_values import StrValue  # pragma: no cover
    from spellbind.int_values import IntValue  # pragma: no cover
    from spellbind.bool_values import BoolValue  # pragma: no cover
    from spellbind.float_values import FloatValue  # pragma: no cover


EMPTY_FROZEN_SET: frozenset = frozenset()

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")
_W = TypeVar("_W")


def _create_value_getter(value: Value[_S] | _S) -> Callable[[], _S]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


class NotConstantError(Exception):
    pass


class Value(Generic[_S], Derived, ABC):
    @property
    @abstractmethod
    def value(self) -> _S: ...

    @property
    @abstractmethod
    def observable(self) -> BiObservable[_S, _S]: ...

    def observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _S],
                times: int | None = None) -> Subscription:
        return self.observable.observe(observer=observer, times=times)

    def weak_observe(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _S],
                     times: int | None = None) -> Subscription:
        return self.observable.weak_observe(observer=observer, times=times)

    def unobserve(self, observer: Observer | ValueObserver[_S] | BiObserver[_S, _S]) -> None:
        self.observable.unobserve(observer=observer)

    def is_observed(self, by: Callable | None = None) -> bool:
        return self.observable.is_observed(by=by)

    def to_str(self) -> StrValue:
        from spellbind.str_values import ToStrValue
        return ToStrValue(self)

    def map(self, transformer: Callable[[_S], _T]) -> Value[_T]:
        return OneToOneValue(transformer, self)

    def map_to_int(self, transformer: Callable[[_S], int]) -> IntValue:
        from spellbind.int_values import OneToIntValue
        return OneToIntValue(transformer, self)

    def map_to_float(self, transformer: Callable[[_S], float]) -> FloatValue:
        from spellbind.float_values import OneToFloatValue
        return OneToFloatValue(transformer, self)

    def map_to_str(self, transformer: Callable[[_S], str]) -> StrValue:
        from spellbind.str_values import OneToStrValue
        return OneToStrValue(transformer, self)

    def map_to_bool(self, transformer: Callable[[_S], bool]) -> BoolValue:
        from spellbind.bool_values import OneToBoolValue
        return OneToBoolValue(transformer, self)

    @property
    def constant_value_or_raise(self) -> _S:
        raise NotConstantError

    def decompose_operands(self, operator_: Callable) -> Sequence[Value[_S] | _S]:
        return (self,)

    @override
    def __str__(self) -> str:
        return str(self.value)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    @classmethod
    def derive_from_two_with_factory(
            cls,
            transformer: Callable[[_S, _T], _U],
            first: _S | Value[_S], second: _T | Value[_T],
            create_value: Callable[[Callable[[_S, _T], _U], _S | Value[_S], _T | Value[_T]], _V],
            create_constant: Callable[[_U], _V]) -> _V:
        try:
            constant_first = get_constant_of_generic_like(first)
            constant_second = get_constant_of_generic_like(second)
        except NotConstantError:
            return create_value(transformer, first, second)
        else:
            return create_constant(transformer(constant_first, constant_second))

    @classmethod
    def derive_from_three_with_factory(
            cls,
            transformer: Callable[[_S, _T, _U], _V],
            first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U],
            create_value: Callable[[Callable[[_S, _T, _U], _V], _S | Value[_S], _T | Value[_T], _U | Value[_U]], _W],
            create_constant: Callable[[_V], _W]) -> _W:
        try:
            constant_first = get_constant_of_generic_like(first)
            constant_second = get_constant_of_generic_like(second)
            constant_third = get_constant_of_generic_like(third)
        except NotConstantError:
            return create_value(transformer, first, second, third)
        else:
            return create_constant(transformer(constant_first, constant_second, constant_third))

    @classmethod
    def derive_three_value(
            cls,
            transformer: Callable[[_S, _T, _U], _V],
            first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> Value[_V]:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToOneValue.create,
            create_constant=Constant.of
        )

    @classmethod
    def derive_from_many_with_factory(
            cls,
            transformer: Callable[[Iterable[_S]], _S], *values: _S | Value[_S],
            create_value: Callable[[Callable[[Iterable[_S]], _S], Sequence[_S | Value[_S]]], _T],
            create_constant: Callable[[_S], _T],
            is_associative: bool = False) -> _T:
        try:
            constant_values = [get_constant_of_generic_like(v) for v in values]
        except NotConstantError:
            if is_associative:
                flattened = tuple(item for v in values for item in decompose_operands_of_generic_like(transformer, v))
                return create_value(transformer, flattened)
            else:
                return create_value(transformer, values)
        else:
            return create_constant(transformer(constant_values))


class Variable(Value[_S], Generic[_S], ABC):
    # mypy 1.17.0 complains that @override is missing, which it is clearly not, so we ignore that error
    @property  # type: ignore[explicit-override]
    @abstractmethod
    @override
    def value(self) -> _S: ...

    @value.setter
    @abstractmethod
    def value(self, new_value: _S) -> None: ...

    @abstractmethod
    def bind(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None: ...

    @deprecated("Use bind() instead")
    def bind_to(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None:
        return self.bind(value, already_bound_ok, bind_weakly)

    @abstractmethod
    def unbind(self, not_bound_ok: bool = False) -> None: ...

    @abstractmethod
    def set_delay_notify(self, new_value: _S) -> ContextManager[None]: ...


class SimpleVariable(Variable[_S], Generic[_S]):
    _bound_to_set: frozenset[Value[_S]]
    _on_change: BiEvent[_S, _S]
    _bound_to: Optional[Value[_S]]

    def __init__(self, value: _S):
        self._bound_to_set = EMPTY_FROZEN_SET
        self._value = value
        self._on_change = BiEvent[_S, _S]()
        self._bound_to = None

    # mypy 1.17.0 complains that @override is missing, which it is clearly not, so we ignore that error
    @property  # type: ignore[explicit-override]
    @override
    def value(self) -> _S:
        return self._value

    @value.setter
    @override
    def value(self, new_value: _S) -> None:
        if self._bound_to is not None:
            raise ValueError("Cannot set value of a Variable that is bound to a Value.")
        self._set_value_bypass_bound_check(new_value)

    @contextmanager
    @override
    def set_delay_notify(self, new_value: _S) -> Generator[None, None, None]:
        if self._bound_to is not None:
            raise ValueError("Cannot set value of a Variable that is bound to a Value.")
        if new_value != self._value:
            old_value = self._value
            self._value = new_value
            yield None
            self._on_change(new_value, old_value)
        else:
            yield None

    def _set_value_bypass_bound_check(self, new_value: _S) -> None:
        if new_value != self._value:
            old_value = self._value
            self._value = new_value
            self._on_change(new_value, old_value)

    @property
    @override
    def observable(self) -> BiObservable[_S, _S]:
        return self._on_change

    @override
    def bind(self, value: Value[_S], already_bound_ok: bool = False, bind_weakly: bool = True) -> None:
        if value is self:
            raise RecursionError("Cannot bind a Variable to itself.")
        if value.is_derived_from(self):
            raise RecursionError("Circular binding detected.")
        if self._bound_to is not None:
            if not already_bound_ok:
                raise ValueError("Variable is already bound to another Value.")
            if self._bound_to is value:
                return
            self.unbind()
        try:
            _ = value.constant_value_or_raise
        except NotConstantError:
            if bind_weakly:
                value.weak_observe(self._set_value_bypass_bound_check)
            else:
                value.observe(self._set_value_bypass_bound_check)
            self._bound_to_set = frozenset([value])
        self._bound_to = value
        self._set_value_bypass_bound_check(value.value)

    @override
    def unbind(self, not_bound_ok: bool = False) -> None:
        if self._bound_to is None:
            if not not_bound_ok:
                raise ValueError("Variable is not bound to any Value.")
            else:
                return

        self._bound_to.unobserve(self._set_value_bypass_bound_check)
        self._bound_to = None
        self._bound_to_set = EMPTY_FROZEN_SET

    @property
    @override
    def derived_from(self) -> frozenset[Value[_S]]:
        return self._bound_to_set


class Constant(Value[_S], Generic[_S]):
    _value: _S

    def __init__(self, value: _S):
        self._value = value

    @property
    @override
    def value(self) -> _S:
        return self._value

    @property
    @override
    def observable(self) -> BiObservable[_S, _S]:
        return void_bi_observable()

    @property
    @override
    def derived_from(self) -> frozenset[Derived]:
        return EMPTY_FROZEN_SET

    @property
    @override
    def deep_derived_from(self) -> Iterable[Derived]:
        return EMPTY_FROZEN_SET

    @override
    def is_derived_from(self, derived: Derived) -> bool:
        return False

    @property
    @override
    def constant_value_or_raise(self) -> _S:
        return self._value

    @classmethod
    def of(cls, value: _S) -> Constant[_S]:
        return Constant(value)

    @override
    def __eq__(self, other):
        if not isinstance(other, Constant):
            return NotImplemented
        return self._value == other._value

    @override
    def __hash__(self):
        return hash(self._value)


class DerivedValueBase(Value[_S], Generic[_S], ABC):
    def __init__(self, *derived_from: Value):
        self._derived_from = frozenset(derived_from)
        self._on_change: BiEvent[_S, _S] = BiEvent[_S, _S]()
        for value in derived_from:
            value.weak_observe(self._on_dependency_changed)
        self._value = self._calculate_value()

    @property
    @override
    def observable(self) -> BiObservable[_S, _S]:
        return self._on_change

    @property
    @override
    def derived_from(self) -> frozenset[Value]:
        return self._derived_from

    def _on_dependency_changed(self) -> None:
        new_value = self._calculate_value()
        if new_value != self._value:
            old_value = self._value
            self._value = new_value
            self._on_change(self._value, old_value)

    @abstractmethod
    def _calculate_value(self) -> _S: ...

    @property
    @override
    def value(self) -> _S:
        return self._value


class OneToOneValue(DerivedValueBase[_T], Generic[_S, _T]):
    _getter: Callable[[], _S]

    def __init__(self, transformer: Callable[[_S], _T], of: Value[_S]):
        self._getter = _create_value_getter(of)
        self._of = of
        self._transformer = transformer
        super().__init__(*[v for v in (of,) if isinstance(v, Value)])

    @override
    def _calculate_value(self) -> _T:
        return self._transformer(self._getter())


class ManyToOneValue(DerivedValueBase[_T], Generic[_S, _T]):
    def __init__(self, transformer: Callable[[Iterable[_S]], _T], *values: _S | Value[_S]):
        self._input_values = tuple(values)
        self._value_getters = [_create_value_getter(v) for v in self._input_values]
        self._transformer = transformer
        super().__init__(*[v for v in self._input_values if isinstance(v, Value)])

    @override
    def _calculate_value(self) -> _T:
        gotten_values = [getter() for getter in self._value_getters]
        return self._transformer(gotten_values)


class ManyToSameValue(ManyToOneValue[_S, _S], Generic[_S]):
    @override
    def decompose_operands(self, transformer: Callable) -> Sequence[Value[_S] | _S]:
        if transformer == self._transformer:
            return self._input_values
        return (self,)


class TwoToOneValue(DerivedValueBase[_U], Generic[_S, _T, _U]):
    def __init__(self, transformer: Callable[[_S, _T], _U],
                 first: Value[_S] | _S, second: Value[_T] | _T):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._first_getter = _create_value_getter(first)
        self._second_getter = _create_value_getter(second)
        super().__init__(*[v for v in (first, second) if isinstance(v, Value)])

    @override
    def _calculate_value(self) -> _U:
        return self._transformer(self._first_getter(), self._second_getter())


class ThreeToOneValue(DerivedValueBase[_V], Generic[_S, _T, _U, _V]):
    def __init__(self, transformer: Callable[[_S, _T, _U], _V],
                 first: Value[_S] | _S, second: Value[_T] | _T, third: Value[_U] | _U):
        self._transformer = transformer
        self._of_first = first
        self._of_second = second
        self._of_third = third
        self._first_getter = _create_value_getter(first)
        self._second_getter = _create_value_getter(second)
        self._third_getter = _create_value_getter(third)
        super().__init__(*[v for v in (first, second, third) if isinstance(v, Value)])

    @override
    def _calculate_value(self) -> _V:
        return self._transformer(self._first_getter(), self._second_getter(), self._third_getter())

    @classmethod
    def create(cls, transformer: Callable[[_S, _T, _U], _V],
               first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> Value[_V]:
        return ThreeToOneValue(transformer, first, second, third)


def get_constant_of_generic_like(value: _S | Value[_S]) -> _S:
    if isinstance(value, Value):
        return value.constant_value_or_raise
    return value


def decompose_operands_of_generic_like(operator_: Callable, value: _S | Value[_S]) -> Sequence[_S | Value[_S]]:
    if isinstance(value, Value):
        return value.decompose_operands(operator_)
    return (value,)
