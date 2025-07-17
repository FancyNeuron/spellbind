from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import zip_longest
from typing import Sequence, Generic, MutableSequence, Iterable, overload, SupportsIndex, Self, Callable, Iterator, \
    TypeVar

from spellbind import int_values
from spellbind.actions import SequenceDeltasAction, ClearAction, ReverseAction, ChangedAction, SequenceDeltaAction, \
    SimpleInsertAction, SimpleExtendAction, SimpleInsertAllAction, SimpleRemoveAtIndexAction, \
    SimpleRemoveAtIndicesAction, SimpleSliceSetAction, SimpleSetAtIndicesAction, \
    SimpleSetAtIndexAction, SimpleSequenceDeltasAction, reverse_action, SimpleChangedAction, DeltaAction, ExtendAction, \
    clear_action
from spellbind.collections import ObservableCollection
from spellbind.event import ValueEvent
from spellbind.int_values import IntVariable, IntValue
from spellbind.observables import ValueObservable, ValuesObservable, void_value_observable, void_values_observable
from spellbind.values import Value, Constant, NotConstantError

_S = TypeVar("_S")
_S_co = TypeVar("_S_co", covariant=True)
_T = TypeVar("_T")


class ObservableSequence(Sequence[_S_co], ObservableCollection[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S_co] | ClearAction[_S_co] | ReverseAction[_S_co] | ChangedAction[_S_co]]: ...

    @abstractmethod
    def map(self, transformer: Callable[[_S_co], _T]) -> ObservableSequence[_T]: ...


class IndexObservableSequence(ObservableSequence[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S_co] | ClearAction[_S_co] | ReverseAction[_S_co]]: ...

    @property
    @abstractmethod
    def delta_observable(self) -> ValuesObservable[SequenceDeltaAction[_S_co]]: ...

    def map(self, transformer: Callable[[_S_co], _T]) -> IndexObservableSequence[_T]:
        return MappedIndexObservableSequence(self, transformer)


class ValueSequence(ObservableSequence[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def on_value_changed(self) -> ValueObservable[SequenceDeltasAction[Value[_S]] | ClearAction[Value[_S]] | ReverseAction[Value[_S]]]: ...


class MutableObservableSequence(ObservableSequence[_S], MutableSequence[_S], Generic[_S], ABC):
    pass


class MutableIndexObservableSequence(IndexObservableSequence[_S], MutableSequence[_S], Generic[_S], ABC):
    pass


class MutableValueSequence(MutableObservableSequence[_S], Generic[_S], ABC):
    @abstractmethod
    def append(self, item: _S | Value[_S]): ...

    @abstractmethod
    def extend(self, items: Iterable[_S | Value[_S]]): ...

    @abstractmethod
    def insert(self, index: SupportsIndex, item: _S | Value[_S]): ...

    @abstractmethod
    def __delitem__(self, key: SupportsIndex | slice): ...

    @abstractmethod
    def clear(self): ...

    @abstractmethod
    def pop(self, index: SupportsIndex = -1) -> _S: ...

    @overload
    @abstractmethod
    def __setitem__(self, key: SupportsIndex, value: _S): ...

    @overload
    @abstractmethod
    def __setitem__(self, key: slice, value: Iterable[_S]): ...

    @abstractmethod
    def __setitem__(self, key, value): ...


class IndexObservableSequenceBase(IndexObservableSequence[_S], Generic[_S]):
    def __init__(self, iterable: Iterable[_S] = ()):
        self._values = list(iterable)
        self._action_event = ValueEvent[SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]()
        self._sequence_deltas_event = ValueEvent[SequenceDeltasAction[_S]]()
        self._delta_observable = self._sequence_deltas_event.map_to_many(
            transformer=lambda deltas_action: deltas_action.delta_actions
        )
        self._len_value = IntVariable(len(self._values))

    @property
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]:
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
            action = SimpleExtendAction(old_length, items)
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
        if self.is_observed():
            with self._len_value.set_delay_notify(new_length):
                action = SimpleInsertAllAction(sorted_index_with_items)
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = new_length

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
        if len(indices) == 0:
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
                action = SimpleRemoveAtIndicesAction(sorted_elements_with_index)
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = len(self._values)

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
                self._sequence_deltas_event(SimpleRemoveAtIndicesAction(removed_elements_with_index))
            if self._action_event.is_observed():
                self._action_event(clear_action())

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

    def _setitem_slice(self, key: slice, values: Iterable[_S]):
        action: SequenceDeltasAction[_S] | None = None
        if self.is_observed():
            old_length = len(self._values)
            # indices = tuple((i + old_length) % old_length for i in range(*key.indices(old_length)))
            indices = tuple(range(*key.indices(old_length)))
            values = tuple(values)
            old_values: tuple[_S, ...]
            if len(indices) == 0:
                if len(values) == 0:
                    return
                indices = (key.start,)
                old_values = ()
            else:
                old_values = tuple(self._values[i] for i in indices)
            if len(old_values) != len(values) or len(values) != len(indices):
                action = SimpleSliceSetAction(indices=indices, new_items=values, old_items=old_values)
            else:
                action = SimpleSetAtIndicesAction(indices_with_new_and_old=tuple(zip(indices, values, old_values)))
        self._values[key] = values
        if action is not None:
            with self._len_value.set_delay_notify(len(self._values)):
                self._action_event(action)
                self._sequence_deltas_event(action)
        else:
            self._len_value.value = len(self._values)

    def _setitem_index(self, key: SupportsIndex, value: _S):
        index = key.__index__()
        old_value = self[index]
        self._values.__setitem__(index, value)
        if not self.is_observed():
            return
        action = SimpleSetAtIndexAction(index, old_item=old_value, new_item=value)
        self._action_event(action)
        self._sequence_deltas_event(action)

    def __eq__(self, other):
        return self._values.__eq__(other)

    def _iadd(self, values: Iterable[_S]) -> Self:  # type: ignore[override, misc]
        self._extend(values)
        return self

    def _mul(self, value: SupportsIndex) -> MutableSequence[_S]:
        mul = value.__index__()
        if mul <= 0:
            return []
        elif mul == 1:
            return [v for v in self]
        return [v for v in self] * mul

    def _imul(self, value: SupportsIndex) -> Self:
        mul = value.__index__()
        if mul <= 0:
            self._clear()
            return self
        elif mul == 1:
            return self
        extend_by = tuple(self._values.__mul__(mul - 1))
        self._extend(extend_by)
        return self

    def _reverse(self):
        if self.length_value.value < 2:
            return
        if self._sequence_deltas_event.is_observed():
            remove_actions = (SimpleRemoveAtIndexAction(0, value) for value in self._values)
            added_actions = (SimpleInsertAction(index, value) for index, value in enumerate(self._values.__reversed__()))
            deltas_action = SimpleSequenceDeltasAction(tuple((*remove_actions, *added_actions)))
        else:
            deltas_action = None
        self._values.reverse()
        if self.is_observed():
            self._action_event(reverse_action())
            if deltas_action is not None:
                self._sequence_deltas_event(deltas_action)

    @property
    def length_value(self) -> IntValue:
        return self._len_value

    def __str__(self):
        return self._values.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._values!r})"


class _ListenerCell(Generic[_S]):
    def __init__(self, value: Value[_S], event: ValueEvent[ChangedAction[_S]]):
        self.value = value
        self.event = event
        self.observe_count = 0
        self.observe(value)

    def observe(self, value: Value[_S]):
        value.weak_observe(self._listener)
        self.observe_count += 1

    def unobserve(self, value: Value[_S]) -> bool:
        value.unobserve(self._listener)
        self.observe_count -= 1
        return self.observe_count == 0

    def _listener(self, new_value: _S, old_value: _S):
        action: ChangedAction[_S] = SimpleChangedAction[_S](new_item=new_value, old_item=old_value)
        self.event(action)


class ValueSequenceBase(ValueSequence[_S], Generic[_S], ABC):
    _full_change_observable: ValueObservable[SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S] | ChangedAction[_S]]
    _on_list_change_observable: ValueObservable[SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]
    _full_delta_observable: ValuesObservable[DeltaAction[_S]]
    _value_changed_delta_observable: ValuesObservable[DeltaAction[_S]]
    _value_list: ObservableList[Value[_S]]
    _listener_cells: dict[Value[_S], _ListenerCell[_S]]

    def __init__(self, values: Iterable[_S | Value[_S]]):
        self._value_changed_event = ValueEvent[ChangedAction[_S]]()

        self._listener_cells = {}
        self._value_list = ObservableList(self._register(v) for v in values)
        self._on_list_change_observable = self._value_list.on_change.map(self._convert_value_list_action)

        self._full_change_observable = self._on_list_change_observable.or_value(self._value_changed_event)

        self._value_changed_delta_observable = self._value_changed_event.map_to_many(lambda a: a.delta_actions)

        derived_delta_observable = self._value_list.delta_observable.map(lambda action: action.map(self._get_value))
        self._full_delta_observable = derived_delta_observable.or_values(self._value_changed_delta_observable)

    def _convert_value_list_action(self,
                                   internal_action: SequenceDeltasAction[Value[_S]] | ClearAction[Value[_S]] | ReverseAction[Value[_S]]
                                   ) -> SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]:
        return internal_action.map(self._get_value)

    def is_observed(self) -> bool:
        return self._value_list.on_change.is_observed() | self._value_list.delta_observable.is_observed()

    @property
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S] | ChangedAction[_S]]:
        return self._full_change_observable

    @property
    def delta_observable(self) -> ValuesObservable[DeltaAction[_S]]:
        return self._full_delta_observable

    @property
    def on_value_changed(self) -> ValueObservable[SequenceDeltasAction[Value[_S]] | ClearAction[Value[_S]] | ReverseAction[Value[_S]]]:
        return self._value_list.on_change

    def _to_constant(self, value: _S) -> Constant[_S]:
        return Constant.of(value)

    def _as_value(self, value: _S | Value[_S]) -> Value[_S]:
        if isinstance(value, Value):
            return value
        return self._to_constant(value)

    def _register(self, v: Value[_S] | _S) -> Value[_S]:
        value = self._as_value(v)
        try:
            _ = value.constant_value_or_raise
            return value  # constants don't get registered/unregistered
        except NotConstantError:
            pass
        try:
            listener_cell = self._listener_cells[value]
        except KeyError:
            self._listener_cells[value] = _ListenerCell(value, self._value_changed_event)
        else:
            listener_cell.observe(value)
        return value

    def _unregister(self, value: Value[_S]):
        try:
            _ = value.constant_value_or_raise
            return  # constants don't get registered/unregistered
        except NotConstantError:
            pass
        listener_cell = self._listener_cells[value]
        if listener_cell.unobserve(value):
            del self._listener_cells[value]

    def _get_value(self, value: Value[_S]) -> _S:
        return value.value

    def _append(self, value: _S | Value[_S]):
        value = self._register(value)
        self._value_list.append(value)

    def _extend(self, values: Iterable[_S | Value[_S]]):
        self._value_list.extend(self._register(value) for value in values)

    def _insert(self, index: SupportsIndex, value: _S | Value[_S]):
        value = self._register(value)
        self._value_list.insert(index, value)

    def _setitem(self, key: SupportsIndex | slice, value: _S | Value[_S]):
        if isinstance(key, SupportsIndex):
            self._setitem_index(key, value)
        else:
            self._setitem_slice(key, value)

    def _setitem_index(self, key: SupportsIndex, value: _S | Value[_S]):
        index = key.__index__()
        self._value_list[index] = self._register(value)

    def _setitem_slice(self, key: slice, values: Iterable[_S | Value[_S]]):
        values = (self._register(value) for value in values)
        self._value_list[key] = values

    def _reverse(self):
        if self.length_value.value < 2:
            return
        self._value_list.reverse()

    @overload
    def __getitem__(self, index: int) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[_S]: ...

    def __getitem__(self, index):
        if isinstance(index, int):
            value = self._value_list[index]
            return value.value
        else:
            return [value.value for value in self._value_list[index]]

    def _insert_all(self, items_with_index: Iterable[tuple[int, _S | Value[_S]]]):
        items_with_index = tuple((i, self._register(item)) for i, item in items_with_index)
        self._value_list.insert_all(items_with_index)

    def _equals_at_index(self, value: _S | Value[_S], index: int, compare_by_value: bool = False) -> bool:
        self_value = self._value_list[index]
        if isinstance(value, Value):
            return self_value == value
        if compare_by_value:
            return self_value.value == value
        try:
            return self_value.constant_value_or_raise == value
        except NotConstantError:
            return False

    def index(self, value: _S | Value[_S], start=0, stop=..., match_by_value: bool = False) -> int:
        for i in range(start, len(self._value_list) if stop is ... else stop):
            if self._equals_at_index(value, i, compare_by_value=match_by_value):
                return i
        raise ValueError(f"Value {value} not found in the list.")

    def _remove(self, item: _S | Value[_S], match_by_value: bool = False):
        index = self.index(item, match_by_value=match_by_value)
        self._delitem_index(index)

    def _remove_all(self, items: Iterable[_S | Value[_S]]):
        self._value_list.remove_all((self._as_value(v) for v in items))

    def _delitem(self, key: SupportsIndex | slice):
        if isinstance(key, slice):
            self._delitem_slice(key)
        else:
            self._delitem_index(key)

    def _delitem_slice(self, key: slice):
        values = self._value_list[key]
        for value in values:
            self._unregister(value)
        del self._value_list[key]

    def _delitem_index(self, key: SupportsIndex):
        value = self._value_list.pop(key)
        self._unregister(value)

    def _clear(self):
        for value in self._value_list:
            self._unregister(value)
        self._value_list.clear()

    def _imul(self, value: SupportsIndex) -> Self:
        index = value.__index__()
        if index <= 0:
            self._clear()
            return self
        elif index == 1:
            return self
        else:
            self._extend(self._value_list * (index - 1))
        return self

    def _iadd(self, other: Iterable[_S | Value[_S]]) -> Self:
        self._value_list += (self._register(item) for item in other)
        return self

    def _pop(self, index: SupportsIndex = -1) -> _S:
        value = self._value_list.pop(index)
        self._unregister(value)
        return value.value

    def __len__(self) -> int:
        return len(self._value_list)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        if not isinstance(other, Sequence):
            return False
        for value_self, v_other in zip(self._value_list, other):
            if isinstance(v_other, Value):
                if value_self != v_other:
                    return False
            else:
                if not value_self.value == v_other:
                    return False
        return True

    def __iter__(self) -> Iterator[_S]:
        for value in self._value_list:
            yield value.value

    @property
    def length_value(self) -> IntValue:
        return self._value_list.length_value

    def __str__(self):
        return '[' + ', '.join(str(x) for x in self._value_list) + ']'

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value_list!r})"


class ValueList(ValueSequenceBase[_S], MutableValueSequence[_S], Generic[_S]):
    def __init__(self, values: Iterable[_S | Value[_S]] = ()):
        super().__init__(values)

    def append(self, item: _S | Value[_S]):
        self._append(item)

    def extend(self, items: Iterable[_S | Value[_S]]):
        self._extend(items)

    def insert(self, index: SupportsIndex, item: _S | Value[_S]):
        self._insert(index, item)

    def map(self, transformer: Callable[[_S], _T]) -> ValueList[_T]:
        raise NotImplementedError

    def remove(self, item: _S | Value[_S]):
        self._remove(item)

    def clear(self):
        self._clear()

    def pop(self, index: SupportsIndex = -1) -> _S:
        return self._pop(index)

    def insert_all(self, items_with_index: Iterable[tuple[int, _S | Value[_S]]]):
        self._insert_all(items_with_index)

    def remove_all(self, items: Iterable[_S]):
        self._remove_all(items)

    def __delitem__(self, key: SupportsIndex | slice):
        self._delitem(key)

    @overload
    def __setitem__(self, key: SupportsIndex, value: _S): ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[_S]): ...

    def __setitem__(self, key, value):
        self._setitem(key, value)

    def __imul__(self, other: SupportsIndex) -> Self:
        return self._imul(other)

    def __iadd__(self, other: Iterable[_S | Value[_S]]) -> Self:
        return self._iadd(other)

    def reverse(self):
        self._reverse()


class ObservableList(IndexObservableSequenceBase[_S], MutableIndexObservableSequence[_S], Generic[_S]):
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

    def __mul__(self, other: SupportsIndex) -> MutableSequence[_S]:
        return self._mul(other)

    def reverse(self):
        self._reverse()


class MappedIndexObservableSequence(IndexObservableSequenceBase[_S], Generic[_S]):
    def __init__(self, mapped_from: IndexObservableSequence[_T], map_func: Callable[[_T], _S]):
        super().__init__(map_func(item) for item in mapped_from)
        self._mapped_from = mapped_from
        self._map_func = map_func

        def on_action(other_action: SequenceDeltasAction[_T] | ClearAction[_T] | ReverseAction[_T]):
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
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S] | ClearAction | ReverseAction]:
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


class _EmptyObservableSequence(IndexObservableSequence[_S], Generic[_S]):
    @property
    def on_change(self) -> ValueObservable[SequenceDeltasAction[_S] | ClearAction | ReverseAction]:
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


EMPTY_SEQUENCE: IndexObservableSequence = _EmptyObservableSequence()


def empty_sequence() -> IndexObservableSequence[_S]:
    return EMPTY_SEQUENCE  # type: ignore[return-value]
