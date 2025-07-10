from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Collection, Sequence, Iterable, SupportsIndex, Iterator, overload, \
    MutableSequence

from typing_extensions import Self

from spellbind import int_values
from spellbind.actions import CollectionAction, SequenceAction, SequenceDeltasAction, \
    SimpleInsertAction, InsertAllAction, SimpleRemoveAtIndexAction, RemoveAtIndicesAction, ExtendAction, \
    clear_sequence_action, SetAtIndexAction, ReverseAction, reverse_sequence_action, ClearAction, \
    SimpleSequenceDeltasAction, SequenceDeltaAction, DeltaAction
from spellbind.event import ValueEvent
from spellbind.int_values import IntVariable, IntValue
from spellbind.observables import ValuesObservable, ValueObservable, void_value_observable, void_values_observable

_S = TypeVar("_S")
_T = TypeVar("_T")


class ObservableCollection(Collection[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[CollectionAction[_S]]: ...

    @property
    @abstractmethod
    def delta_observable(self) -> ValuesObservable[DeltaAction[_S]]: ...

    @property
    @abstractmethod
    def length_value(self) -> IntValue: ...

    def __len__(self) -> int:
        return self.length_value.value


class ObservableSequence(Sequence[_S], ObservableCollection[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[SequenceAction[_S]]: ...

    @property
    @abstractmethod
    def delta_observable(self) -> ValuesObservable[SequenceDeltaAction[_S]]: ...


class ObservableMutableSequence(ObservableSequence[_S], MutableSequence[_S], Generic[_S], ABC):
    pass


class ObservableSequenceBase(ObservableSequence[_S], Generic[_S]):
    def __init__(self, iterable: Iterable[_S] = ()):
        self._values = list(iterable)
        self._action_event = ValueEvent[SequenceAction[_S]]()
        self._sequence_deltas_event = ValueEvent[SequenceDeltasAction[_S]]()
        self._delta_observable = self._sequence_deltas_event.derive_many(
            transformer=lambda deltas_action: deltas_action.delta_actions
        )
        self._len_value = IntVariable(len(self._values))

    @property
    def on_change(self) -> ValueObservable[SequenceAction[_S]]:
        return self._action_event

    @property
    def delta_observable(self) -> ValuesObservable[SequenceDeltaAction[_S]]:
        return self._delta_observable

    @overload
    def __getitem__(self, index: SupportsIndex) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[_S]: ...

    def __getitem__(self, index):
        return self._values[index]

    def _append(self, item: _S):
        self._values.append(item)
        new_length = len(self._values)
        if self.is_observed():
            with self._len_value.set_delay_notify(new_length):
                action = SimpleInsertAction(new_length - 1, item)
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = new_length

    def is_observed(self):
        return self._action_event.is_observed() or self._sequence_deltas_event.is_observed()

    def _extend(self, items: Iterable[_S]):
        old_length = len(self._values)
        observed = self.is_observed()
        if observed:
            items = tuple(items)
            action = ExtendAction(old_length, items)
        else:
            action = None
        self._values.extend(items)
        new_length = len(self._values)
        if old_length == new_length:
            return
        if action is not None:
            with self._len_value.set_delay_notify(new_length):
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = new_length

    def _insert(self, index: SupportsIndex, item: _S):
        self._values.insert(index, item)
        if self.is_observed():
            with self._len_value.set_delay_notify(len(self._values)):
                action = SimpleInsertAction(index.__index__(), item)
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = len(self._values)

    def _insert_all(self, index_with_items: Iterable[tuple[int, _S]]):
        index_with_items = tuple(index_with_items)
        sorted_index_with_items = tuple(sorted(index_with_items, key=lambda x: x[0]))
        old_length = len(self._values)
        for index, item in reversed(sorted_index_with_items):
            # TODO: handle index out of range and undo successful inserts
            self._values.insert(index, item)
        new_length = len(self._values)
        if old_length == new_length:
            return
        with self._len_value.set_delay_notify(new_length):
            if self.is_observed():
                action = InsertAllAction(sorted_index_with_items)
                self._action_event(action)
                self._sequence_deltas_event(action)

    def _remove(self, item: _S):
        index = self.index(item)
        self._delitem_index(index)

    def _delitem(self, key: SupportsIndex | slice):
        if isinstance(key, slice):
            self._delitem_slice(key)
        else:
            self._delitem_index(key)

    def _delitem_index(self, key: SupportsIndex):
        index = key.__index__()
        item = self[index]
        self._values.__delitem__(index)
        if self.is_observed():
            with self._len_value.set_delay_notify(len(self._values)):
                action = SimpleRemoveAtIndexAction(index, item)
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = len(self._values)

    def _delitem_slice(self, slice_key: slice):
        indices = range(*slice_key.indices(len(self._values)))
        if not indices:
            return
        self._del_all(indices)

    def indices_of(self, items: Iterable[_S]) -> Iterable[int]:
        last_indices: dict[_S, int] = {}
        for item in items:
            last_index = last_indices.get(item, 0)
            index = self.index(item, last_index)
            last_indices[item] = index + 1
            yield index

    def _del_all(self, indices: Iterable[SupportsIndex]):
        indices_ints: tuple[int, ...] = tuple(index.__index__() for index in indices)
        if len(indices_ints) == 0:
            return

        reverse_sorted_indices = sorted(indices_ints, reverse=True)
        reverse_elements_with_index: tuple[tuple[int, _S], ...] = tuple((i, self._values.pop(i)) for i in reverse_sorted_indices)
        if self.is_observed():
            with self._len_value.set_delay_notify(len(self._values)):
                sorted_elements_with_index: tuple[tuple[int, _S], ...] = tuple(reversed(reverse_elements_with_index))
                action = RemoveAtIndicesAction(sorted_elements_with_index)
                self._action_event(action)
                self._sequence_deltas_event(action)

    def _remove_all(self, items: Iterable[_S]):
        indices_to_remove = list(self.indices_of(items))
        self._del_all(indices_to_remove)

    def _clear(self):
        if self._sequence_deltas_event.is_observed():
            removed_elements_with_index = tuple((enumerate(self)))
        else:
            removed_elements_with_index = None
        self._values.clear()

        with self._len_value.set_delay_notify(0):
            if removed_elements_with_index is not None:
                self._sequence_deltas_event(RemoveAtIndicesAction(removed_elements_with_index))
            if self._action_event.is_observed():
                self._action_event(clear_sequence_action())

    def _pop(self, index: SupportsIndex = -1) -> _S:
        index = index.__index__()
        if index < 0:
            index += len(self._values)
        item = self[index]
        self._delitem_index(index)
        return item

    @overload
    def _setitem(self, key: SupportsIndex, value: _S): ...

    @overload
    def _setitem(self, key: slice, value: Iterable[_S]): ...

    def _setitem(self, key, value):
        if isinstance(key, slice):
            self._setitem_slice(key, value)
        else:
            self._setitem_index(key, value)

    def __eq__(self, other):
        return self._values.__eq__(other)

    def _setitem_slice(self, key: slice, value: Iterable[_S]):
        raise NotImplementedError

    def _setitem_index(self, key: SupportsIndex, value: _S):
        index = key.__index__()
        old_value = self[index]
        self._values.__setitem__(index, value)
        if not self.is_observed():
            return
        action = SetAtIndexAction(index, old_value, value)
        self._action_event(action)
        self._sequence_deltas_event(action)

    def _iadd(self, values: Iterable[_S]) -> Self:  # type: ignore[override, misc]
        self._extend(values)
        return self

    def _imul(self, value: SupportsIndex) -> Self:
        mul = value.__index__()
        if mul == 0:
            self._clear()
            return self
        elif mul == 1:
            return self
        extend_by = tuple(self._values.__mul__(mul - 1))
        self._extend(extend_by)
        return self

    def _reverse(self):
        if self._sequence_deltas_event.is_observed():
            remove_actions = (SimpleRemoveAtIndexAction(0, value) for value in self._values)
            added_actions = (SimpleInsertAction(index, value) for index, value in enumerate(self._values.__reversed__()))
            deltas_action = SimpleSequenceDeltasAction(tuple((*remove_actions, *added_actions)))
        else:
            deltas_action = None
        self._values.reverse()
        if self.is_observed():
            self._action_event(reverse_sequence_action())
            if deltas_action is not None:
                self._sequence_deltas_event(deltas_action)

    def map(self, transformer: Callable[[_S], _T]) -> ObservableSequence[_T]:
        return MappedObservableSequence(self, transformer)

    @property
    def length_value(self) -> IntValue:
        return self._len_value

    def __str__(self):
        return self._values.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._values!r})"


class ObservableList(ObservableSequenceBase[_S], ObservableMutableSequence[_S], Generic[_S]):
    def append(self, item: _S):
        self._append(item)

    def extend(self, items: Iterable[_S]):
        self._extend(items)

    def insert(self, index: SupportsIndex, item: _S):
        self._insert(index, item)

    def insert_all(self, items_with_index: Iterable[tuple[int, _S]]):
        self._insert_all(items_with_index)

    def remove(self, item: _S):
        self._remove(item)

    def __delitem__(self, key: SupportsIndex | slice):
        self._delitem(key)

    def del_all(self, indices: Iterable[SupportsIndex]):
        self._del_all(indices)

    def remove_all(self, items: Iterable[_S]):
        self._remove_all(items)

    def clear(self):
        self._clear()

    def pop(self, index: SupportsIndex = -1) -> _S:
        return self._pop(index)

    @overload
    def __setitem__(self, key: SupportsIndex, value: _S): ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[_S]): ...

    def __setitem__(self, key, value):
        self._setitem(key, value)

    def __iadd__(self, values: Iterable[_S]) -> Self:  # type: ignore[override, misc]
        return self._iadd(values)

    def __imul__(self, value: SupportsIndex) -> Self:
        return self._imul(value)

    def reverse(self):
        self._reverse()


class MappedObservableSequence(ObservableSequenceBase[_S], Generic[_S]):
    def __init__(self, mapped_from: ObservableSequence[_T], map_func: Callable[[_T], _S]):
        super().__init__(map_func(item) for item in mapped_from)
        self._mapped_from = mapped_from
        self._map_func = map_func

        def on_action(other_action: SequenceAction[_T]):
            if isinstance(other_action, SequenceDeltasAction):
                if isinstance(other_action, ExtendAction):
                    self._extend((self._map_func(item) for item in other_action.items))
                else:
                    for delta in other_action.delta_actions:
                        if delta.is_add:
                            value = self._map_func(delta.value)
                            self._values.insert(delta.index, value)
                        else:
                            del self._values[delta.index]
                if self._is_observed():
                    with self._len_value.set_delay_notify(len(self._values)):
                        action = other_action.map(self._map_func)
                        self._action_event(action)
                        self._sequence_deltas_event(action)
                else:
                    self._len_value.value = len(self._values)
            elif isinstance(other_action, ClearAction):
                self._clear()
            elif isinstance(other_action, ReverseAction):
                self._reverse()

        mapped_from.on_change.observe(on_action)

    def _is_observed(self):
        return self._action_event.is_observed() or self._sequence_deltas_event.is_observed()

    @property
    def on_change(self) -> ValueObservable[SequenceAction[_S]]:
        return self._action_event

    @property
    def delta_observable(self) -> ValuesObservable[SequenceDeltaAction[_S]]:
        return self._delta_observable

    @property
    def length_value(self) -> IntValue:
        return self._len_value

    def __iter__(self) -> Iterator[_S]:
        return iter(self._values)

    @overload
    def __getitem__(self, index: SupportsIndex) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[_S]: ...

    def __getitem__(self, index):
        return self._values[index]


class _EmptyObservableSequence(ObservableSequence[_S], Generic[_S]):
    @property
    def on_change(self) -> ValueObservable[SequenceAction[_S]]:
        return void_value_observable()

    @property
    def delta_observable(self) -> ValuesObservable[SequenceDeltaAction[_S]]:
        return void_values_observable()

    @property
    def length_value(self) -> IntValue:
        return int_values.ZERO

    @property
    def added_observable(self) -> ValueObservable[_S]:
        return void_value_observable()

    @property
    def added_index_observable(self) -> ValueObservable[tuple[int, _S]]:
        return void_value_observable()

    @property
    def removed_observable(self) -> ValueObservable[_S]:
        return void_value_observable()

    @property
    def removed_index_observable(self) -> ValueObservable[tuple[int, _S]]:
        return void_value_observable()

    def __len__(self) -> int:
        return 0

    @overload
    def __getitem__(self, index: int) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_S]: ...

    def __getitem__(self, index):
        raise IndexError("Empty sequence has no items")

    def __iter__(self) -> Iterator[_S]:
        return iter(())

    def __contains__(self, item) -> bool:
        return False

    def __str__(self):
        return "[]"


EMPTY_SEQUENCE: ObservableSequence = _EmptyObservableSequence()


def empty_sequence() -> ObservableSequence[_S]:
    return EMPTY_SEQUENCE  # type: ignore[return-value]
