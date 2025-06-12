from __future__ import annotations

import operator
from abc import ABC
from typing import TypeVar, Generic

from spellbind.values import Value, OneToOneValue, Constant, SimpleVariable

_S = TypeVar('_S')


class BoolValue(Value[bool], ABC):
    def logical_not(self) -> BoolValue:
        return NotBoolValue(self)


class OneToBoolValue(OneToOneValue[_S, bool], BoolValue, Generic[_S]):
    pass


class NotBoolValue(OneToOneValue[bool, bool], BoolValue):
    def __init__(self, value: Value[bool]):
        super().__init__(operator.not_, value)


class BoolConstant(BoolValue, Constant[bool]):
    pass


class BoolVariable(SimpleVariable[bool], BoolValue):
    pass


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
