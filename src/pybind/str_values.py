from __future__ import annotations

from abc import ABC
from typing import Any

from pybind.values import Value, DerivedValue, CombinedValue, SimpleVariable

StringLike = str | Value[str]


class StrValue(Value[str], ABC):
    def __add__(self, other: Value[str]) -> StrValue:
        return ConcatenateStrValues(self, other)


class StrVariable(SimpleVariable[str], StrValue):
    pass


class ToStrValue(DerivedValue[Any, str], StrValue):
    def transform(self, s: Any) -> str:
        return str(s)

    def to_str(self) -> StrValue:
        return self


class ConcatenateStrValues(CombinedValue[str, str], StrValue):
    def __init__(self, *values: StringLike):
        super().__init__(values)

    def transform(self, *values: str) -> str:
        return ''.join(value for value in values)
