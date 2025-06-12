from __future__ import annotations

import math
import operator
from abc import ABC
from typing import overload, Generic

from typing_extensions import Self, TypeVar

from spellbind.bool_values import BoolValue, BoolLike
from spellbind.float_values import FloatValue, MultiplyFloatValues, DivideValues, SubtractFloatValues, \
    AddFloatValues, CompareNumbersValues
from spellbind.functions import clamp_int, multiply_all_ints
from spellbind.values import Value, ManyToOneValue, SimpleVariable, TwoToOneValue, OneToOneValue, Constant, \
    ThreeToOneValue, SelectValue

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

    def clamp(self, min_value: IntLike, max_value: IntLike) -> IntValue:
        return ClampIntValue(self, min_value, max_value)


class OneToIntValue(Generic[_S], OneToOneValue[_S, int], IntValue):
    pass


class IntConstant(IntValue, Constant[int]):
    pass


class IntVariable(SimpleVariable[int], IntValue):
    pass


class MaxIntValues(ManyToOneValue[int, int], IntValue):
    def __init__(self, *values: IntLike):
        super().__init__(max, *values)


class MinIntValues(ManyToOneValue[int, int], IntValue):
    def __init__(self, *values: IntLike):
        super().__init__(min, *values)


class AddIntValues(ManyToOneValue[int, int], IntValue):
    def __init__(self, *values: IntLike):
        super().__init__(sum, *values)


class SubtractIntValues(TwoToOneValue[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(operator.sub, left, right)


class MultiplyIntValues(ManyToOneValue[int, int], IntValue):
    def __init__(self, *values: IntLike):
        super().__init__(multiply_all_ints, *values)


class FloorDivideIntValues(TwoToOneValue[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(operator.floordiv, left, right)


class PowerIntValues(TwoToOneValue[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(operator.pow, left, right)


class ModuloIntValues(TwoToOneValue[int, int, int], IntValue):
    def __init__(self, left: IntLike, right: IntLike):
        super().__init__(operator.mod, left, right)


class AbsIntValue(OneToOneValue[int, int], IntValue):
    def __init__(self, value: Value[int]):
        super().__init__(abs, value)


class NegateIntValue(OneToOneValue[int, int], IntValue):
    def __init__(self, value: Value[int]):
        super().__init__(operator.neg, value)


class FloorFloatValue(OneToOneValue[float, int], IntValue):
    def __init__(self, value: Value[float]):
        super().__init__(math.floor, value)


class CeilFloatValue(OneToOneValue[float, int], IntValue):
    def __init__(self, value: Value[float]):
        super().__init__(math.ceil, value)


class RoundFloatToIntValue(OneToOneValue[float, int], IntValue):
    def __init__(self, value: Value[float]):
        super().__init__(round, value)


class ClampIntValue(ThreeToOneValue[int, int, int, int], IntValue):
    def __init__(self, value: IntLike, min_value: IntLike, max_value: IntLike) -> None:
        super().__init__(clamp_int, value, min_value, max_value)


class SelectIntValue(SelectValue[int], IntValue):
    def __init__(self, condition: BoolLike, if_true: IntLike, if_false: IntLike):
        super().__init__(condition, if_true, if_false)
