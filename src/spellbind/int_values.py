from __future__ import annotations
from typing_extensions import Self, TypeVar

import math
import operator
from abc import ABC
from typing import overload, Generic, Callable

from spellbind.float_values import FloatValue, MultiplyFloatValues, DivideValues, SubtractFloatValues, \
    AddFloatValues, CompareNumbersValues
from spellbind.values import Value, CombinedMixedValues, SimpleVariable, CombinedTwoValues, DerivedValue, Constant
from spellbind.bool_values import BoolValue

IntLike = int | Value[int]
FloatLike = IntLike | float | FloatValue


_S = TypeVar('_S')


class IntValue(Value[int], ABC):
    @overload
    def __add__(self, other: IntLike) -> IntValue: ...

    @overload
    def __add__(self, other: float | FloatValue) -> FloatValue: ...

    def __add__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return AddFloatValues(self, other)
        return AddIntValues(self, other)

    @overload
    def __radd__(self, other: int) -> IntValue: ...

    @overload
    def __radd__(self, other: float) -> FloatValue: ...

    def __radd__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return AddFloatValues(other, self)
        return AddIntValues(other, self)

    @overload
    def __sub__(self, other: IntLike) -> IntValue: ...

    @overload
    def __sub__(self, other: float | FloatValue) -> FloatValue: ...

    def __sub__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return SubtractFloatValues(self, other)
        return SubtractIntValues(self, other)

    @overload
    def __rsub__(self, other: int) -> IntValue: ...

    @overload
    def __rsub__(self, other: float) -> FloatValue: ...

    def __rsub__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return SubtractFloatValues(other, self)
        return SubtractIntValues(other, self)

    @overload
    def __mul__(self, other: IntLike) -> IntValue: ...

    @overload
    def __mul__(self, other: float | FloatValue) -> FloatValue: ...

    def __mul__(self, other: FloatLike) -> IntValue | FloatValue:
        if isinstance(other, (float, FloatValue)):
            return MultiplyFloatValues(self, other)
        return MultiplyIntValues(self, other)

    @overload
    def __rmul__(self, other: int) -> IntValue: ...

    @overload
    def __rmul__(self, other: float) -> FloatValue: ...

    def __rmul__(self, other: int | float) -> IntValue | FloatValue:
        if isinstance(other, float):
            return MultiplyFloatValues(other, self)
        return MultiplyIntValues(other, self)

    def __truediv__(self, other: FloatLike) -> FloatValue:
        return DivideValues(self, other)

    def __rtruediv__(self, other: int | float) -> FloatValue:
        return DivideValues(other, self)

    def __floordiv__(self, other: IntLike) -> IntValue:
        return FloorDivideIntValues(self, other)

    def __rfloordiv__(self, other: int) -> IntValue:
        return FloorDivideIntValues(other, self)

    def __pow__(self, other: IntLike) -> IntValue:
        return PowerIntValues(self, other)

    def __rpow__(self, other: int) -> IntValue:
        return PowerIntValues(other, self)

    def __mod__(self, other: IntLike) -> IntValue:
        return ModuloIntValues(self, other)

    def __rmod__(self, other: int) -> IntValue:
        return ModuloIntValues(other, self)

    def __abs__(self) -> IntValue:
        return AbsIntValue(self)

    def __lt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.lt)

    def __le__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.le)

    def __gt__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.gt)

    def __ge__(self, other: FloatLike) -> BoolValue:
        return CompareNumbersValues(self, other, operator.ge)

    def __neg__(self) -> IntValue:
        return NegateIntValue(self)

    def __pos__(self) -> Self:
        return self


class MappedIntValue(Generic[_S], DerivedValue[_S, int], IntValue):
    def __init__(self, value: Value[_S], transform: Callable[[_S], int]) -> None:
        self._transform = transform
        super().__init__(value)

    def transform(self, value: _S) -> int:
        return self._transform(value)


class IntConstant(IntValue, Constant[int]):
    pass


class IntVariable(SimpleVariable[int], IntValue):
    pass


class MaxIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        return max(values)


class MinIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        return min(values)


class AddIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        return sum(values)


class SubtractIntValues(CombinedTwoValues[int, int, int], IntValue):
    def transform(self, left: int, right: int) -> int:
        return left - right


class MultiplyIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        result = 1
        for value in values:
            result *= value
        return result


class DivideIntValues(CombinedTwoValues[int, int, float], FloatValue):
    def transform(self, left: int, right: int) -> float:
        return left / right


class FloorDivideIntValues(CombinedTwoValues[int, int, int], IntValue):
    def transform(self, left: int, right: int) -> int:
        return left // right


class PowerIntValues(CombinedTwoValues[int, int, int], IntValue):
    def transform(self, left: int, right: int) -> int:
        return left ** right


class ModuloIntValues(CombinedTwoValues[int, int, int], IntValue):
    def transform(self, left: int, right: int) -> int:
        return left % right


class AbsIntValue(DerivedValue[int, int], IntValue):
    def transform(self, value: int) -> int:
        return abs(value)


class NegateIntValue(DerivedValue[int, int], IntValue):
    def transform(self, value: int) -> int:
        return -value


class FloorFloatValue(DerivedValue[float, int], IntValue):
    def transform(self, value: float) -> int:
        return math.floor(value)


class CeilFloatValue(DerivedValue[float, int], IntValue):
    def transform(self, value: float) -> int:
        return math.ceil(value)


class RoundFloatToIntValue(DerivedValue[float, int], IntValue):
    def transform(self, value: float) -> int:
        return round(value)
