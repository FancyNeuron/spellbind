from __future__ import annotations

from abc import ABC
from typing import Any, Generic, Callable, TypeVar

from spellbind.values import Value, DerivedValue, CombinedMixedValues, SimpleVariable, Constant

StringLike = str | Value[str]

_S = TypeVar('_S')


class StrValue(Value[str], ABC):
    def __add__(self, other: StringLike) -> StrValue:
        return ConcatenateStrValues(self, other)

    def __radd__(self, other: StringLike) -> StrValue:
        return ConcatenateStrValues(other, self)


class MappedStrValue(Generic[_S], DerivedValue[_S, str], StrValue):
    def __init__(self, value: Value[_S], transform: Callable[[_S], str]) -> None:
        self._transform = transform
        super().__init__(value)

    def transform(self, value: _S) -> str:
        return self._transform(value)


class StrConstant(StrValue, Constant[str]):
    pass


class StrVariable(SimpleVariable[str], StrValue):
    pass


class ToStrValue(DerivedValue[Any, str], StrValue):
    def transform(self, value: Any) -> str:
        return str(value)

    def to_str(self) -> StrValue:
        return self


class ConcatenateStrValues(CombinedMixedValues[str, str], StrValue):
    def transform(self, *values: str) -> str:
        return ''.join(value for value in values)
