from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Collection, Callable, Iterable, Iterator

from spellbind.actions import CollectionAction, DeltaAction, DeltasAction, ClearAction
from spellbind.event import BiEvent
from spellbind.int_values import IntValue
from spellbind.observables import ValuesObservable, ValueObservable, BiObservable
from spellbind.str_values import StrValue
from spellbind.values import Value, EMPTY_FROZEN_SET

_S = TypeVar("_S")
_S_co = TypeVar("_S_co", covariant=True)
_T = TypeVar("_T")


class ObservableCollection(Collection[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[CollectionAction[_S_co]]: ...

    @property
    @abstractmethod
    def delta_observable(self) -> ValuesObservable[DeltaAction[_S_co]]: ...

    @property
    @abstractmethod
    def length_value(self) -> IntValue: ...

    def __len__(self) -> int:
        return self.length_value.value

    def combine(self, combiner: Callable[[Iterable[_S_co]], _S]) -> Value[_S]:
        return CombinedValue(self, combiner=combiner)

    def combine_to_str(self, combiner: Callable[[Iterable[_S_co]], str]) -> StrValue:
        from spellbind.str_collections import CombinedStrValue

        return CombinedStrValue(self, combiner=combiner)

    def combine_to_int(self, combiner: Callable[[Iterable[_S_co]], int]) -> IntValue:
        from spellbind.int_collections import CombinedIntValue

        return CombinedIntValue(self, combiner=combiner)

    def reduce(self,
               add_reducer: Callable[[_T, _S_co], _T],
               remove_reducer: Callable[[_T, _S_co], _T],
               initial: _T) -> Value[_T]:
        from spellbind.str_collections import ReducedValue

        return ReducedValue(self,
                            add_reducer=add_reducer,
                            remove_reducer=remove_reducer,
                            initial=initial)

    def reduce_to_str(self,
                      add_reducer: Callable[[str, _S_co], str],
                      remove_reducer: Callable[[str, _S_co], str],
                      initial: str) -> StrValue:
        from spellbind.str_collections import ReducedStrValue

        return ReducedStrValue(self,
                               add_reducer=add_reducer,
                               remove_reducer=remove_reducer,
                               initial=initial)

    def reduce_to_int(self,
                      add_reducer: Callable[[int, _S_co], int],
                      remove_reducer: Callable[[int, _S_co], int],
                      initial: int) -> IntValue:
        from spellbind.int_collections import ReducedIntValue

        return ReducedIntValue(self,
                               add_reducer=add_reducer,
                               remove_reducer=remove_reducer,
                               initial=initial)


class ReducedValue(Value[_S], Generic[_S]):
    def __init__(self,
                 collection: ObservableCollection[_T],
                 add_reducer: Callable[[_S, _T], _S],
                 remove_reducer: Callable[[_S, _T], _S],
                 initial: _S):
        super().__init__()
        self._collection = collection
        self._add_reducer = add_reducer
        self._removed_reducer = remove_reducer
        self._initial = initial
        self._value = functools.reduce(self._add_reducer, self._collection, self._initial)
        self._collection.on_change.observe(self._on_action)
        self._on_change: BiEvent[_S, _S] = BiEvent[_S, _S]()

    def _on_action(self, action: CollectionAction[_T]):
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
            self._set_value(self._initial)

    def _set_value(self, value: _S):
        if self._value != value:
            old_value = self._value
            self._value = value
            self._on_change(value, old_value)

    @property
    def value(self) -> _S:
        return self._value

    @property
    def observable(self) -> BiObservable[_S, _S]:
        return self._on_change

    @property
    def derived_from(self) -> frozenset[Value]:
        return EMPTY_FROZEN_SET


class ValueCollection(ObservableCollection[Value[_S]], Generic[_S], ABC):
    def reduce_to_int(self,
                      add_reducer: Callable[[int, Value[_S]], int],
                      remove_reducer: Callable[[int, Value[_S]], int],
                      initial: int) -> IntValue:
        from spellbind.int_collections import ReducedIntValue

        return ReducedIntValue(self,
                               add_reducer=add_reducer,
                               remove_reducer=remove_reducer,
                               initial=initial)

    def value_iterable(self) -> Iterable[_S]:
        return (value.value for value in self)

    def value_iter(self) -> Iterator[_S]:
        return iter(self.value_iterable())


class CombinedValue(Value[_S], Generic[_S]):
    def __init__(self, collection: ObservableCollection[_T], combiner: Callable[[Iterable[_T]], _S]):
        super().__init__()
        self._collection = collection
        self._combiner = combiner
        self._value = self._combiner(self._collection)
        self._collection.on_change.observe(self._recalculate_value)
        self._on_change: BiEvent[_S, _S] = BiEvent[_S, _S]()

    @property
    def observable(self) -> BiObservable[_S, _S]:
        return self._on_change

    def _recalculate_value(self):
        old_value = self._value
        self._value = self._combiner(self._collection)
        if self._value != old_value:
            self._on_change(self._value, old_value)

    @property
    def value(self) -> _S:
        return self._value

    @property
    def derived_from(self) -> frozenset[Value]:
        return EMPTY_FROZEN_SET
