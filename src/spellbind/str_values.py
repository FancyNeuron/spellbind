from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

from spellbind.bool_values import BoolLike, StrLike
from spellbind.values import Value, OneToOneValue, ManyToOneValue, SimpleVariable, Constant, SelectValue

StringLike = str | Value[str]

_S = TypeVar('_S')


class StrValue(Value[str], ABC):
    def __add__(self, other: StringLike) -> StrValue:
        return ConcatenateStrValues(self, other)

    def __radd__(self, other: StringLike) -> StrValue:
        return ConcatenateStrValues(other, self)

    def to_str(self) -> StrValue:
        return self


class OneToStrValue(OneToOneValue[_S, str], StrValue, Generic[_S]):
    pass


class StrConstant(Constant[str], StrValue):
    pass


class StrVariable(SimpleVariable[str], StrValue):
    pass


class ToStrValue(OneToOneValue[Any, str], StrValue):
    def __init__(self, value: Value[Any]):
        super().__init__(str, value)


class ConcatenateStrValues(ManyToOneValue[str, str], StrValue):
    def __init__(self, *values: StringLike):
        super().__init__(''.join, *values)


class SelectStrValue(SelectValue[str], StrValue):
    def __init__(self, condition: BoolLike, if_true: StrLike, if_false: StrLike):
        super().__init__(condition, if_true, if_false)
