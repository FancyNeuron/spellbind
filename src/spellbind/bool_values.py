from __future__ import annotations

import operator
from abc import ABC
from typing import TypeVar, Generic, overload, TYPE_CHECKING, TypeAlias
from spellbind.values import Value, OneToOneValue, Constant, SimpleVariable, TwoToOneValue, SelectValue

if TYPE_CHECKING:
    from spellbind.float_values import FloatValue  # pragma: no cover
    from spellbind.int_values import IntValue  # pragma: no cover
    from spellbind.str_values import StrValue  # pragma: no cover

IntValueLike: TypeAlias = 'IntValue | int'
FloatValueLike: TypeAlias = 'FloatValue | float'
StrValueLike: TypeAlias = 'StrValue | str'
BoolValueLike: TypeAlias = 'BoolValue | bool'

_S = TypeVar('_S')

BoolLike = bool | Value[bool]
IntLike = int | Value[int]
FloatLike = float | Value[float]
StrLike = str | Value[str]


class BoolValue(Value[bool], ABC):
    def logical_not(self) -> BoolValue:
        return NotBoolValue(self)

    def __and__(self, other: BoolLike) -> BoolValue:
        return AndBoolValues(self, other)

    def __rand__(self, other: bool) -> BoolValue:
        return AndBoolValues(other, self)

    def __or__(self, other: BoolLike) -> BoolValue:
        return OrBoolValues(self, other)

    def __ror__(self, other: bool) -> BoolValue:
        return OrBoolValues(other, self)

    def __xor__(self, other: BoolLike) -> BoolValue:
        return XorBoolValues(self, other)

    def __rxor__(self, other: bool) -> BoolValue:
        return XorBoolValues(other, self)

    @overload
    def select(self, if_true: IntValueLike, if_false: IntValueLike) -> IntValue: ...

    @overload
    def select(self, if_true: FloatValueLike, if_false: FloatValueLike) -> FloatValue: ...

    @overload
    def select(self, if_true: StrValueLike, if_false: StrValueLike) -> StrValue: ...

    @overload
    def select(self, if_true: BoolValue, if_false: BoolValue) -> BoolValue: ...

    @overload
    def select(self, if_true: Value[_S] | _S, if_false: Value[_S] | _S) -> Value[_S]: ...

    def select(self, if_true, if_false):
        from spellbind.float_values import FloatValue, SelectFloatValue
        from spellbind.int_values import IntValue, SelectIntValue
        from spellbind.str_values import StrValue, SelectStrValue

        if isinstance(if_true, (FloatValue, float)) and isinstance(if_false, (FloatValue, float)):
            return SelectFloatValue(self, if_true, if_false)
        elif isinstance(if_true, (StrValue, str)) and isinstance(if_false, (StrValue, str)):
            return SelectStrValue(self, if_true, if_false)
        elif isinstance(if_true, (BoolValue, bool)) and isinstance(if_false, (BoolValue, bool)):
            return SelectBoolValue(self, if_true, if_false)
        elif isinstance(if_true, (IntValue, int)) and isinstance(if_false, (IntValue, int)):
            return SelectIntValue(self, if_true, if_false)
        else:
            return SelectValue(self, if_true, if_false)


class OneToBoolValue(OneToOneValue[_S, bool], BoolValue, Generic[_S]):
    pass


class NotBoolValue(OneToOneValue[bool, bool], BoolValue):
    def __init__(self, value: Value[bool]):
        super().__init__(operator.not_, value)


class AndBoolValues(TwoToOneValue[bool, bool, bool], BoolValue):
    def __init__(self, left: BoolLike, right: BoolLike):
        super().__init__(operator.and_, left, right)


class OrBoolValues(TwoToOneValue[bool, bool, bool], BoolValue):
    def __init__(self, left: BoolLike, right: BoolLike):
        super().__init__(operator.or_, left, right)


class XorBoolValues(TwoToOneValue[bool, bool, bool], BoolValue):
    def __init__(self, left: BoolLike, right: BoolLike):
        super().__init__(operator.xor, left, right)


class BoolConstant(BoolValue, Constant[bool]):
    pass


class BoolVariable(SimpleVariable[bool], BoolValue):
    pass


class SelectBoolValue(SelectValue[bool], BoolValue):
    def __init__(self, condition: BoolLike, if_true: BoolLike, if_false: BoolLike):
        super().__init__(condition, if_true, if_false)


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
