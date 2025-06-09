from __future__ import annotations

from abc import ABC

from spellbind.values import Value, DerivedValue, Constant


class BoolValue(Value[bool], ABC):
    def logical_not(self) -> BoolValue:
        return NotBoolValue(self)


class NotBoolValue(DerivedValue[bool, bool], BoolValue):
    def __init__(self, value: Value[bool]):
        super().__init__(value)

    def transform(self, value: bool) -> bool:
        return not value


class BoolConstant(BoolValue, Constant[bool]):
    pass


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
