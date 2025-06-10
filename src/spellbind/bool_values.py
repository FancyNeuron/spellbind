from __future__ import annotations

from abc import ABC
from typing import TypeVar, Generic, Callable

from spellbind.values import Value, DerivedValue, Constant, SimpleVariable

_S = TypeVar('_S')


class BoolValue(Value[bool], ABC):
    def logical_not(self) -> BoolValue:
        return NotBoolValue(self)


class MappedBoolValue(Generic[_S], DerivedValue[_S, bool], BoolValue):
    def __init__(self, value: Value[_S], transform: Callable[[_S], bool]) -> None:
        self._transform = transform
        super().__init__(value)

    def transform(self, value: _S) -> bool:
        return self._transform(value)


class NotBoolValue(DerivedValue[bool, bool], BoolValue):
    def __init__(self, value: Value[bool]):
        super().__init__(value)

    def transform(self, value: bool) -> bool:
        return not value


class BoolConstant(BoolValue, Constant[bool]):
    pass


class BoolVariable(SimpleVariable[bool], BoolValue):
    pass


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
