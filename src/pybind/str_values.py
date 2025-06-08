from __future__ import annotations

from abc import ABC
from typing import Any

from pybind.values import Value, DerivedValue, CombinedMixedValues, SimpleVariable

StringLike = str | Value[str]


class StrValue(Value[str], ABC):
    def __add__(self, other: Value[str]) -> StrValue:
        return ConcatenateStrValues(self, other)


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
