from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Collection

from spellbind.actions import CollectionAction, DeltaAction
from spellbind.int_values import IntValue
from spellbind.observables import ValuesObservable, ValueObservable

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
