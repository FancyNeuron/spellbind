from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Optional, Any, Iterable

from pybind.event import ValueEvent
from pybind.observables import ValueObservable, Observer, ValueObserver

EMPTY_FROZEN_SET: frozenset = frozenset()

_S = TypeVar("_S")


class Value(ValueObservable[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def value(self) -> _S:
        raise NotImplementedError

    @abstractmethod
    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
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
    def bind_to(self, value: Value[_S], already_bound_ok: bool = False) -> None:
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

    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        self._on_change.observe(observer)

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        self._on_change.unobserve(observer)

    def bind_to(self, value: Value[_S], already_bound_ok: bool = False) -> None:
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

    def observe(self, observer: Observer | ValueObserver[_S]) -> None:
        pass

    def unobserve(self, observer: Observer | ValueObserver[_S]) -> None:
        pass

    def derived_from(self) -> frozenset[Value[_S]]:
        return EMPTY_FROZEN_SET
