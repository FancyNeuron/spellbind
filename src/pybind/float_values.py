from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Callable, Sequence

from pybind.event import ValueEvent
from pybind.observables import Observer, ValueObserver

from pybind.values import Value, CombinedValue, SimpleVariable, CombinedTwoValues, _U, _create_value_getter

FloatLike = int | Value[int] | float | Value[float]


class FloatValue(Value[float], ABC):
    def __add__(self, other: FloatLike) -> FloatValue:
        return AddFloatValues(self, other)

    def __radd__(self, other: int | float) -> FloatValue:
        return AddFloatValues(other, self)

    def __sub__(self, other: FloatLike) -> FloatValue:
        return SubtractFloatValues(self, other)

    def __rsub__(self, other: int | float) -> FloatValue:
        return SubtractFloatValues(other, self)

    def __mul__(self, other: FloatLike) -> FloatValue:
        return MultiplyFloatValues(self, other)

    def __rmul__(self, other: int | float) -> FloatValue:
        return MultiplyFloatValues(other, self)

    def __truediv__(self, other: FloatLike) -> FloatValue:
        return DivideValues(self, other)

    def __rtruediv__(self, other: int | float) -> FloatValue:
        return DivideValues(other, self)


def _create_float_getter(value: float | Value[int] | Value[float]) -> Callable[[], float]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


def _get_float(value: float | Value[int] | Value[float]) -> float:
    if isinstance(value, Value):
        return value.value
    else:
        return value


class CombinedManyFloatValues(Value[_U], Generic[_U], ABC):
    def __init__(self, *values: float | Value[int] | Value[float]):
        self.gotten_values = [_get_float(v) for v in values]
        listed_values = []
        for i, v in enumerate(values):
            if isinstance(v, Value):
                listed_values.append(v)
                v.observe(self._create_on_n_changed(i))
        self._value = self._calculate_value()
        self._on_change: ValueEvent[_U] = ValueEvent()
        self._value_sources = frozenset(listed_values)

    def _create_on_n_changed(self, index: int) -> Callable[[float], None]:
        def on_change(new_value: float) -> None:
            self.gotten_values[index] = new_value
            self._on_result_change(self._calculate_value())
        return on_change

    def _calculate_value(self) -> _U:
        return self.transform(self.gotten_values)

    def _on_result_change(self, new_value: _U) -> None:
        if new_value != self._value:
            self._value = new_value
            self._on_change(self._value)

    @abstractmethod
    def transform(self, values: Sequence[float]) -> _U:
        raise NotImplementedError

    @property
    def value(self) -> _U:
        return self._value

    def observe(self, observer: Observer | ValueObserver[_U]) -> None:
        self._on_change.observe(observer)

    def unobserve(self, observer: Observer | ValueObserver[_U]) -> None:
        self._on_change.unobserve(observer)

    def derived_from(self) -> frozenset[Value]:
        return self._value_sources


class CombinedTwoFloatValues(CombinedManyFloatValues[_U], Generic[_U], ABC):
    def __init__(self,
                 left: float | Value[int] | Value[float],
                 right: float | Value[int] | Value[float]):
        super().__init__(left, right)

    def transform(self, values: Sequence[float]) -> _U:
        return self.transform_two(values[0], values[1])

    @abstractmethod
    def transform_two(self, left: float, right: float) -> _U:
        raise NotImplementedError


class AddFloatValues(CombinedManyFloatValues[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(*values)

    def transform(self, values: Sequence[float]) -> float:
        return sum(values)


class SubtractFloatValues(CombinedTwoFloatValues[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(left, right)

    def transform_two(self, left: float, right: float) -> float:
        return left - right


class MultiplyFloatValues(CombinedManyFloatValues[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(*values)

    def transform(self, values: Sequence[float]) -> float:
        result = 1.0
        for value in values:
            result *= value
        return result


class DivideValues(CombinedTwoFloatValues[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(left, right)

    def transform_two(self, left: float, right: float) -> float:
        return left / right


class FloatVariable(SimpleVariable[float], FloatValue):
    pass
