from abc import ABC
from typing import Iterable, Callable, Any

from typing_extensions import TypeIs

from spellbind.int_values import IntValue
from spellbind.observable_collections import ObservableCollection, ReducedValue, CombinedValue
from spellbind.observable_sequences import ObservableList, _S, TypedValueList
from spellbind.str_values import StrValue, StrConstant
from spellbind.values import Value


class ObservableStrCollection(ObservableCollection[str], ABC):
    @property
    def concatenated(self) -> StrValue:
        return self.combine_to_str(combiner="".join)

    @property
    def summed_lengths(self) -> IntValue:
        return self.reduce_to_int(add_reducer=lambda acc, s: acc + len(s),
                                  remove_reducer=lambda acc, s: acc - len(s),
                                  initial=0)


class ObservableStrList(ObservableList[str], ObservableStrCollection):
    pass


class CombinedStrValue(CombinedValue[str], StrValue):
    def __init__(self, collection: ObservableCollection[_S], combiner: Callable[[Iterable[_S]], str]) -> None:
        super().__init__(collection=collection, combiner=combiner)


class ReducedStrValue(ReducedValue[str], StrValue):
    def __init__(self,
                 collection: ObservableCollection[_S],
                 add_reducer: Callable[[str, _S], str],
                 remove_reducer: Callable[[str, _S], str],
                 initial: str):
        super().__init__(collection=collection,
                         add_reducer=add_reducer,
                         remove_reducer=remove_reducer,
                         initial=initial)


class StrValueList(TypedValueList[str], ObservableStrCollection):
    def __init__(self, values: Iterable[str | Value[str]] | None = None):
        def is_str(value: Any) -> TypeIs[str]:
            return isinstance(value, str)
        super().__init__(values, checker=is_str, constant_factory=StrConstant.of)
