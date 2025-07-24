from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Iterable, Callable, Any, TypeVar

from typing_extensions import TypeIs, override

from spellbind.int_values import IntValue, IntConstant
from spellbind.observable_collections import ObservableCollection, ReducedValue, CombinedValue, ValueCollection
from spellbind.observable_sequences import ObservableList, TypedValueList, ValueSequence, UnboxedValueSequence, \
    ObservableSequence
from spellbind.values import Value


_S = TypeVar("_S")


class ObservableIntCollection(ObservableCollection[int], ABC):
    @property
    def summed(self) -> IntValue:
        return self.reduce_to_int(add_reducer=operator.add, remove_reducer=operator.sub, initial=0)

    @property
    def multiplied(self) -> IntValue:
        return self.reduce_to_int(add_reducer=operator.mul, remove_reducer=operator.floordiv, initial=1)


class ObservableIntSequence(ObservableSequence[int], ObservableIntCollection, ABC):
    pass


class ObservableIntList(ObservableList[int], ObservableIntSequence):
    pass


class IntValueCollection(ValueCollection[int], ABC):
    @property
    def summed(self) -> IntValue:
        return self.unboxed.reduce_to_int(add_reducer=operator.add, remove_reducer=operator.sub, initial=0)

    @property
    @abstractmethod
    def unboxed(self) -> ObservableIntCollection: ...


class CombinedIntValue(CombinedValue[int], IntValue):
    def __init__(self, collection: ObservableCollection[_S], combiner: Callable[[Iterable[_S]], int]) -> None:
        super().__init__(collection=collection, combiner=combiner)


class ReducedIntValue(ReducedValue[int], IntValue):
    def __init__(self,
                 collection: ObservableCollection[_S],
                 add_reducer: Callable[[int, _S], int],
                 remove_reducer: Callable[[int, _S], int],
                 initial: int):
        super().__init__(collection=collection,
                         add_reducer=add_reducer,
                         remove_reducer=remove_reducer,
                         initial=initial)


class UnboxedIntValueSequence(UnboxedValueSequence[int], ObservableIntSequence):
    def __init__(self, sequence: IntValueSequence) -> None:
        super().__init__(sequence)


class IntValueSequence(ValueSequence[int], IntValueCollection, ABC):
    @cached_property
    @override
    def unboxed(self) -> ObservableIntSequence:
        return UnboxedIntValueSequence(self)


class IntValueList(TypedValueList[int], IntValueSequence):
    def __init__(self, values: Iterable[int | Value[int]] | None = None):
        def is_int(value: Any) -> TypeIs[int]:
            return isinstance(value, int)
        super().__init__(values, checker=is_int, constant_factory=IntConstant.of)
