from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Iterable, Callable, Any, TypeVar

from typing_extensions import TypeIs, override

from spellbind.float_values import FloatValue, FloatConstant
from spellbind.observable_collections import ObservableCollection, ReducedValue, CombinedValue, ValueCollection, \
    MappedObservableBag
from spellbind.observable_sequences import ObservableList, TypedValueList, ValueSequence, UnboxedValueSequence, \
    ObservableSequence
from spellbind.values import Value


_S = TypeVar("_S")


class ObservableFloatCollection(ObservableCollection[float], ABC):
    @property
    def summed(self) -> FloatValue:
        return self.reduce_to_float(add_reducer=operator.add, remove_reducer=operator.sub, initial=0.0)

    @property
    def multiplied(self) -> FloatValue:
        return self.reduce_to_float(add_reducer=operator.mul, remove_reducer=operator.truediv, initial=1.0)


class MappedToFloatBag(MappedObservableBag[float], ObservableFloatCollection):
    pass


class ObservableFloatSequence(ObservableSequence[float], ObservableFloatCollection, ABC):
    pass


class ObservableFloatList(ObservableList[float], ObservableFloatSequence):
    pass


class FloatValueCollection(ValueCollection[float], ABC):
    @property
    def summed(self) -> FloatValue:
        return self.unboxed.reduce_to_float(add_reducer=operator.add, remove_reducer=operator.sub, initial=0.0)

    @property
    @abstractmethod
    def unboxed(self) -> ObservableFloatCollection: ...


class CombinedFloatValue(CombinedValue[float], FloatValue):
    def __init__(self, collection: ObservableCollection[_S], combiner: Callable[[Iterable[_S]], float]) -> None:
        super().__init__(collection=collection, combiner=combiner)


class ReducedFloatValue(ReducedValue[float], FloatValue):
    def __init__(self,
                 collection: ObservableCollection[_S],
                 add_reducer: Callable[[float, _S], float],
                 remove_reducer: Callable[[float, _S], float],
                 initial: float):
        super().__init__(collection=collection,
                         add_reducer=add_reducer,
                         remove_reducer=remove_reducer,
                         initial=initial)


class UnboxedFloatValueSequence(UnboxedValueSequence[float], ObservableFloatSequence):
    def __init__(self, sequence: FloatValueSequence) -> None:
        super().__init__(sequence)


class FloatValueSequence(ValueSequence[float], FloatValueCollection, ABC):
    @cached_property
    @override
    def unboxed(self) -> ObservableFloatSequence:
        return UnboxedFloatValueSequence(self)


class FloatValueList(TypedValueList[float], FloatValueSequence):
    def __init__(self, values: Iterable[float | Value[float]] | None = None):
        def is_float(value: Any) -> TypeIs[float]:
            return isinstance(value, float)
        super().__init__(values, checker=is_float, constant_factory=FloatConstant.of)
