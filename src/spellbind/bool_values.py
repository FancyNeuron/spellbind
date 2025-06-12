from __future__ import annotations

import operator
from abc import ABC
from typing import TypeVar, Generic

from spellbind.values import Value, OneToOneValue, Constant, SimpleVariable, TwoToOneValue

_S = TypeVar('_S')

BoolLike = Value[bool] | bool


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


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
