from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from typing import Generic, Callable, Sequence, TypeVar, overload

from typing_extensions import Self
from typing_extensions import TYPE_CHECKING

from spellbind.bool_values import BoolValue
from spellbind.values import Value, SimpleVariable, DerivedValue, DerivedValueBase, Constant, CombinedTwoValues

if TYPE_CHECKING:
    from spellbind.int_values import IntValue, IntLike

FloatLike = Value[int] | float | Value[float]

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

    def __pow__(self, other: FloatLike) -> FloatValue:
        return PowerFloatValues(self, other)

    def __rpow__(self, other: FloatLike) -> FloatValue:
        return PowerFloatValues(other, self)

    def __mod__(self, other: FloatLike) -> FloatValue:
        return ModuloFloatValues(self, other)

    def __rmod__(self, other: int | float) -> FloatValue:
        return ModuloFloatValues(other, self)

    def __abs__(self) -> FloatValue:
        return AbsFloatValue(self)

    def floor(self) -> IntValue:
        from spellbind.int_values import FloorFloatValue
        return FloorFloatValue(self)

    def ceil(self) -> IntValue:
        from spellbind.int_values import CeilFloatValue
        return CeilFloatValue(self)

    @overload
    def round(self) -> IntValue: ...

    @overload
    def round(self, ndigits: IntLike) -> FloatValue: ...

    def round(self, ndigits: IntLike | None = None) -> FloatValue | IntValue:
        if ndigits is None:
            from spellbind.int_values import RoundFloatToIntValue
            return RoundFloatToIntValue(self)
        return RoundFloatValue(self, ndigits)

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

    def __pos__(self) -> Self:
        return self


class MappedFloatValue(Generic[_S], DerivedValue[_S, float], FloatValue):
    def __init__(self, value: Value[_S], transform: Callable[[_S], float]) -> None:
        self._transform = transform
        super().__init__(value)

    def transform(self, value: _S) -> float:
        return self._transform(value)


class FloatConstant(FloatValue, Constant[float]):
    pass


class FloatVariable(SimpleVariable[float], FloatValue):
    pass


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
        self._gotten_values = [_get_float(v) for v in values]
        self._callbacks: list[Callable] = []
        for i, v in enumerate(values):
            if isinstance(v, Value):
                v.weak_observe(self._create_on_n_changed(i))
        self._value = self._calculate_value()

    def _create_on_n_changed(self, index: int) -> Callable[[float], None]:
        def on_change(new_value: float) -> None:
            self._gotten_values[index] = new_value
            self._on_result_change(self._calculate_value())
        self._callbacks.append(on_change)  # keep strong reference to callback so it won't be garbage collected
        return on_change

    def _calculate_value(self) -> _U:
        return self.transform(self._gotten_values)

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


class MaxFloatValues(CombinedFloatValues[float], FloatValue):
    def transform(self, values: Sequence[float]) -> float:
        return max(values)


class MinFloatValues(CombinedFloatValues[float], FloatValue):
    def transform(self, values: Sequence[float]) -> float:
        return min(values)


class CombinedTwoFloatValues(CombinedFloatValues[_U], Generic[_U], ABC):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(left, right)

    def transform(self, values: Sequence[float]) -> _U:
        return self.transform_two(values[0], values[1])

    @abstractmethod
    def transform_two(self, left: float, right: float) -> _U:
        raise NotImplementedError


class AddFloatValues(CombinedFloatValues[float], FloatValue):
    def transform(self, values: Sequence[float]) -> float:
        return sum(values)


class SubtractFloatValues(CombinedTwoFloatValues[float], FloatValue):
    def transform_two(self, left: float, right: float) -> float:
        return left - right


class MultiplyFloatValues(CombinedFloatValues[float], FloatValue):
    def transform(self, values: Sequence[float]) -> float:
        result = 1.0
        for value in values:
            result *= value
        return result


class DivideValues(CombinedTwoFloatValues[float], FloatValue):
    def transform_two(self, left: float, right: float) -> float:
        return left / right


class RoundFloatValue(CombinedTwoValues[float, int, float], FloatValue):
    def __init__(self, value: FloatValue, ndigits: IntLike):
        super().__init__(value, ndigits)

    def transform(self, value: float, ndigits: int) -> float:
        return round(value, ndigits)


class ModuloFloatValues(CombinedTwoFloatValues[float], FloatValue):
    def transform_two(self, left: float, right: float) -> float:
        return left % right


class AbsFloatValue(DerivedValue[float, float], FloatValue):
    def transform(self, value: float) -> float:
        return abs(value)


class PowerFloatValues(CombinedTwoFloatValues[float], FloatValue):
    def transform_two(self, left: float, right: float) -> float:
        return left ** right


class NegateFloatValue(DerivedValue[float, float], FloatValue):
    def transform(self, value: float) -> float:
        return -value


class CompareNumbersValues(CombinedTwoFloatValues[bool], BoolValue):
    def __init__(self, left: FloatLike, right: FloatLike, op: Callable[[float, float], bool]):
        self._op = op
        super().__init__(left, right)

    def transform_two(self, left: float, right: float) -> bool:
        return self._op(left, right)
