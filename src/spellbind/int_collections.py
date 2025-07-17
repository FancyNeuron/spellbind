import operator
from abc import ABC
from functools import reduce
from typing import Iterable, Callable

from spellbind.actions import CollectionAction, ClearAction, DeltasAction
from spellbind.collections import ObservableCollection
from spellbind.sequences import ObservableList
from spellbind.event import BiEvent
from spellbind.int_values import IntValue
from spellbind.observables import BiObservable
from spellbind.values import Value, EMPTY_FROZEN_SET


class ObservableIntCollection(ObservableCollection[int], ABC):
    def reduce(self,
               add_reducer: Callable[[int, int], int],
               remove_reducer: Callable[[int, int], int],
               empty_value: int) -> IntValue:
        return CommutativeCombinedIntValue(self,
                                           add_reducer=add_reducer,
                                           remove_reducer=remove_reducer,
                                           empty_value=empty_value)

    def sum(self) -> IntValue:
        return self.reduce(add_reducer=operator.add, remove_reducer=operator.sub, empty_value=0)

    def multiply(self) -> IntValue:
        return self.reduce(add_reducer=operator.mul, remove_reducer=operator.floordiv, empty_value=1)


class ObservableIntList(ObservableList[int], ObservableIntCollection):
    pass


class IntValueFromCollectionBase(IntValue, ABC):
    def __init__(self):
        self._on_change: BiEvent[int, int] = BiEvent[int, int]()

    @property
    def observable(self) -> BiObservable[int, int]:
        return self._on_change

    @property
    def derived_from(self) -> frozenset[Value]:
        return EMPTY_FROZEN_SET


class SimpleCombinedIntValue(IntValueFromCollectionBase):
    def __init__(self, collection: ObservableCollection[int], combiner: Callable[[Iterable[int]], int]):
        super().__init__()
        self._collection = collection
        self._combiner = combiner
        self._value = self._combiner(self._collection)
        self._collection.on_change.observe(self._recalculate_value)

    def _recalculate_value(self):
        self._value = self._combiner(self._collection)

    @property
    def value(self) -> int:
        return self._value


class CommutativeCombinedIntValue(IntValueFromCollectionBase):
    def __init__(self, collection: ObservableCollection[int], add_reducer: Callable[[int, int], int],
                 remove_reducer: Callable[[int, int], int], empty_value: int):
        super().__init__()
        self._collection = collection
        self._add_reducer = add_reducer
        self._removed_reducer = remove_reducer
        self._empty_value = empty_value
        self._value = reduce(self._add_reducer, self._collection, self._empty_value)
        self._collection.on_change.observe(self._on_action)

    def _on_action(self, action: CollectionAction[int]):
        if action.is_permutation_only:
            return
        if isinstance(action, DeltasAction):
            value = self._value
            for delta_action in action.delta_actions:
                if delta_action.is_add:
                    value = self._add_reducer(value, delta_action.value)
                else:
                    value = self._removed_reducer(value, delta_action.value)
            self._set_value(value)
        elif isinstance(action, ClearAction):
            self._set_value(self._empty_value)

    def _set_value(self, value: int):
        if self._value != value:
            old_value = self._value
            self._value = value
            self._on_change(value, old_value)

    @property
    def value(self) -> int:
        return self._value
