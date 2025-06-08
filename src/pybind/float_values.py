from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from typing import Generic, Callable, Sequence, TypeVar

from pybind.bool_values import BoolValue
from pybind.event import ValueEvent
from pybind.observables import Observer, ValueObserver

from pybind.values import Value, CombinedMixedValues, SimpleVariable, CombinedTwoValues, _create_value_getter, \
    DerivedValue, DerivedValueBase


FloatLike = int | Value[int] | float | Value[float]

_S = TypeVar("_S")
_T = TypeVar("_T")
_U = TypeVar("_U")


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

    def __lt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.lt)

    def __le__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.le)

    def __gt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.gt)

    def __ge__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.ge)

    def __neg__(self) -> FloatValue:
        return NegateFloatValue(self)


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


class CombinedFloatValues(DerivedValueBase[_U], Generic[_U], ABC):
    def __init__(self, *values: float | Value[int] | Value[float]):
        super().__init__(*[v for v in values if isinstance(v, Value)])
        self.gotten_values = [_get_float(v) for v in values]
        for i, v in enumerate(values):
            if isinstance(v, Value):
                v.observe(self._create_on_n_changed(i))
        self._value = self._calculate_value()
        self._on_change: ValueEvent[_U] = ValueEvent()

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


class CombinedTwoFloatValues(CombinedFloatValues[_U], Generic[_U], ABC):
    def __init__(self,
                 left: float | Value[int] | Value[float],
                 right: float | Value[int] | Value[float]):
        super().__init__(left, right)

    def transform(self, values: Sequence[float]) -> _U:
        return self.transform_two(values[0], values[1])

    @abstractmethod
    def transform_two(self, left: float, right: float) -> _U:
        raise NotImplementedError


class AddFloatValues(CombinedFloatValues[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(*values)

    def transform(self, values: Sequence[float]) -> float:
        return sum(values)


class SubtractFloatValues(CombinedTwoFloatValues[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(left, right)

    def transform_two(self, left: float, right: float) -> float:
        return left - right


class MultiplyFloatValues(CombinedFloatValues[float], FloatValue):
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


class NegateFloatValue(DerivedValue[float, float], FloatValue):
    def transform(self, value: float) -> float:
        return -value


class CompareNumbersValues(CombinedTwoFloatValues[bool], BoolValue):
    def __init__(self, left: FloatLike, right: FloatLike, op: Callable[[float, float], bool]):
        self._op = op
        super().__init__(left, right)

    def transform_two(self, left: float, right: float) -> bool:
        return self._op(left, right)
