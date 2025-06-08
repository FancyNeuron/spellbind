from __future__ import annotations

import operator
from abc import ABC
from typing import overload

from pybind.float_values import FloatValue, MultiplyFloatValues, DivideValues, SubtractFloatValues, \
    AddFloatValues, CompareNumbersValues
from pybind.values import Value, CombinedMixedValues, SimpleVariable, CombinedTwoValues, DerivedValue, Constant
from pybind.bool_values import BoolValue

IntLike = int | Value[int]
FloatLike = IntLike | float | FloatValue


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


class IntConstant(IntValue, Constant[int]):
    pass


class IntVariable(SimpleVariable[int], IntValue):
    pass


class AddIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        return sum(values)


class SubtractIntValues(CombinedTwoValues[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(left, right)

    def transform(self, left: int, right: int) -> int:
        return left - right


class MultiplyIntValues(CombinedMixedValues[int, int], IntValue):
    def transform(self, *values: int) -> int:
        result = 1
        for value in values:
            result *= value
        return result


class DivideIntValues(CombinedTwoValues[int, int, float], FloatValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(left, right)

    def transform(self, left: int, right: int) -> float:
        return left / right


class FloorDivideIntValues(CombinedTwoValues[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(left, right)

    def transform(self, left: int, right: int) -> int:
        return left // right


class NegateIntValue(DerivedValue[int, int], IntValue):
    def transform(self, value: int) -> int:
        return -value
