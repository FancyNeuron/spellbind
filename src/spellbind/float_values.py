from __future__ import annotations

import operator
from abc import ABC
from typing import Generic, Callable, Sequence, TypeVar, overload

from typing_extensions import Self
from typing_extensions import TYPE_CHECKING

from spellbind.bool_values import BoolValue, BoolLike
from spellbind.functions import clamp_float, multiply_all_floats
from spellbind.values import Value, SimpleVariable, OneToOneValue, DerivedValueBase, Constant, TwoToOneValue, \
    SelectValue

if TYPE_CHECKING:
    from spellbind.int_values import IntValue, IntLike  # pragma: no cover

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

    def clamp(self, min_value: FloatLike, max_value: FloatLike) -> FloatValue:
        return ClampFloatValue(self, min_value, max_value)


class OneToFloatValue(Generic[_S], OneToOneValue[_S, float], FloatValue):
    pass


class FloatConstant(FloatValue, Constant[float]):
    pass


class FloatVariable(SimpleVariable[float], FloatValue):
    pass


def _create_float_getter(value: float | Value[int] | Value[float]) -> Callable[[], float]:
    if isinstance(value, Value):
        return lambda: value.value
    else:
        return lambda: value


class OneFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float], _S], of: FloatLike):
        self._getter = _create_float_getter(of)
        self._transformer = transformer
        super().__init__(*[v for v in (of,) if isinstance(v, Value)])

    @property
    def value(self) -> _S:
        return self._value

    def _calculate_value(self) -> _S:
        return self._transformer(self._getter())


class ManyFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[Sequence[float]], _S], *values: FloatLike):
        self._value_getters = [_create_float_getter(v) for v in values]
        self._transformer = transformer
        super().__init__(*[v for v in values if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        gotten_values = [getter() for getter in self._value_getters]
        return self._transformer(gotten_values)


class TwoFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float, float], _S],
                 first: FloatLike, second: FloatLike):
        self._transformer = transformer
        self._first_getter = _create_float_getter(first)
        self._second_getter = _create_float_getter(second)
        super().__init__(*[v for v in (first, second) if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        return self._transformer(self._first_getter(), self._second_getter())


class ThreeFloatToOneValue(DerivedValueBase[_S], Generic[_S]):
    def __init__(self, transformer: Callable[[float, float, float], _S],
                 first: FloatLike, second: FloatLike, third: FloatLike):
        self._transformer = transformer
        self._first_getter = _create_float_getter(first)
        self._second_getter = _create_float_getter(second)
        self._third_getter = _create_float_getter(third)
        super().__init__(*[v for v in (first, second, third) if isinstance(v, Value)])

    def _calculate_value(self) -> _S:
        return self._transformer(self._first_getter(), self._second_getter(), self._third_getter())


class MaxFloatValues(ManyFloatToOneValue[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(max, *values)


class MinFloatValues(ManyFloatToOneValue[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(min, *values)


class AddFloatValues(ManyFloatToOneValue[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(sum, *values)


class SubtractFloatValues(TwoFloatToOneValue[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(operator.sub, left, right)


class MultiplyFloatValues(ManyFloatToOneValue[float], FloatValue):
    def __init__(self, *values: FloatLike):
        super().__init__(multiply_all_floats, *values)


class RoundFloatValue(TwoToOneValue[float, int, float], FloatValue):
    def __init__(self, value: FloatValue, ndigits: IntLike):
        super().__init__(round, value, ndigits)


class DivideValues(TwoFloatToOneValue[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(operator.truediv, left, right)


class ModuloFloatValues(TwoFloatToOneValue[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(operator.mod, left, right)


class AbsFloatValue(OneFloatToOneValue[float], FloatValue):
    def __init__(self, value: FloatLike):
        super().__init__(abs, value)


class PowerFloatValues(TwoFloatToOneValue[float], FloatValue):
    def __init__(self, left: FloatLike, right: FloatLike):
        super().__init__(operator.pow, left, right)


class NegateFloatValue(OneFloatToOneValue[float], FloatValue):
    def __init__(self, value: FloatLike):
        super().__init__(operator.neg, value)


class CompareNumbersValues(TwoFloatToOneValue[bool], BoolValue):
    def __init__(self, left: FloatLike, right: FloatLike, op: Callable[[float, float], bool]):
        super().__init__(op, left, right)


class ClampFloatValue(ThreeFloatToOneValue[float], FloatValue):
    def __init__(self, value: FloatLike, min_value: FloatLike, max_value: FloatLike):
        super().__init__(clamp_float, value, min_value, max_value)


class SelectFloatValue(SelectValue[float], FloatValue):
    def __init__(self, condition: BoolLike, if_true: float | Value[float], if_false: float | Value[float]):
        super().__init__(condition, if_true, if_false)
