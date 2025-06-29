from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar, Callable, Sequence, Iterable, TYPE_CHECKING

from spellbind.bool_values import BoolLike
from spellbind.values import Value, OneToOneValue, SimpleVariable, Constant, SelectValue, \
    ManyToSameValue, NotConstantError, get_constant_of_generic_like, decompose_operands_of_generic_like


if TYPE_CHECKING:
    from spellbind.int_values import IntValue, IntConstant  # pragma: no cover


StrLike = str | Value[str]

_S = TypeVar('_S')


def _join_strs(values: Iterable[str]) -> str:
    return "".join(values)


class StrValue(Value[str], ABC):
    def __add__(self, other: StrLike) -> StrValue:
        return StrValue.derive_many(_join_strs, self, other, is_associative=True)

    def __radd__(self, other: StrLike) -> StrValue:
        return StrValue.derive_many(_join_strs, other, self, is_associative=True)

    @property
    def length(self) -> IntValue:
        from spellbind.int_values import IntValue
        str_length: Callable[[str], int] = len
        return IntValue.derive_one(str_length, self)

    def to_str(self) -> StrValue:
        return self

    @classmethod
    def derive_many(cls, operator_: Callable[[Iterable[str]], str], *values: StrLike,
                    is_associative: bool = False) -> StrValue:
        try:
            constant_values = [get_constant_of_generic_like(v) for v in values]
        except NotConstantError:
            if is_associative:
                flattened = tuple(item for v in values for item in decompose_operands_of_generic_like(operator_, v))
                return ManyStrsToStrValue(operator_, *flattened)
            else:
                return ManyStrsToStrValue(operator_, *values)
        else:
            return StrConstant.of(operator_(constant_values))


class OneToStrValue(OneToOneValue[_S, str], StrValue, Generic[_S]):
    pass


class StrConstant(Constant[str], StrValue):
    _cache: dict[str, StrConstant] = {}

    @classmethod
    def of(cls, value: str, cache: bool = False) -> StrConstant:
        try:
            return cls._cache[value]
        except KeyError:
            constant = StrConstant(value)
            if cache:
                cls._cache[value] = constant
            return constant

    @property
    def length(self) -> IntConstant:
        from spellbind.int_values import IntConstant
        return IntConstant.of(len(self.value))


EMPTY_STRING = StrConstant.of("")

for _number_value in [*range(10)]:
    StrConstant.of(str(_number_value), cache=True)

for _alpha_value in "abcdefghijklmnopqrstuvwxyz":
    StrConstant.of(_alpha_value, cache=True)
    StrConstant.of(_alpha_value.upper(), cache=True)

for _special_char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/":
    StrConstant.of(_special_char, cache=True)


class StrVariable(SimpleVariable[str], StrValue):
    pass


class ManyStrsToStrValue(ManyToSameValue[str], StrValue):
    def __init__(self, transformer: Callable[[Sequence[str]], str], *values: StrLike):
        super().__init__(transformer, *values)


class ToStrValue(OneToOneValue[Any, str], StrValue):
    def __init__(self, value: Value[Any]):
        super().__init__(str, value)


class SelectStrValue(SelectValue[str], StrValue):
    def __init__(self, condition: BoolLike, if_true: StrLike, if_false: StrLike):
        super().__init__(condition, if_true, if_false)
