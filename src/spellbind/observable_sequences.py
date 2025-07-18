from __future__ import annotations

from functools import cached_property

from typing_extensions import TypeIs, Self

from abc import ABC, abstractmethod
from typing import Sequence, Generic, MutableSequence, Iterable, overload, SupportsIndex, Callable, Iterator, \
    TypeVar, Any

from spellbind import int_values
from spellbind.actions import AtIndicesDeltasAction, ClearAction, ReverseAction, OneElementChangedAction, \
    AtIndexDeltaAction, \
    SimpleInsertAction, SimpleExtendAction, SimpleInsertAllAction, SimpleRemoveAtIndexAction, \
    SimpleRemoveAtIndicesAction, SimpleSliceSetAction, SimpleSetAtIndicesAction, \
    SimpleSetAtIndexAction, SimpleAtIndicesDeltasAction, reverse_action, ExtendAction, \
    clear_action, DeltaAction, SimpleRemoveOneAction, SimpleAddOneAction, ElementsChangedAction, \
    SimpleOneElementChangedAction
from spellbind.event import ValueEvent
from spellbind.int_values import IntVariable, IntValue
from spellbind.observable_collections import ObservableCollection, ValueCollection
from spellbind.observables import ValueObservable, ValuesObservable, void_value_observable, void_values_observable
from spellbind.values import Value, NotConstantError, Constant

_S = TypeVar("_S")
_S_co = TypeVar("_S_co", covariant=True)
_T = TypeVar("_T")


class ObservableSequence(Sequence[_S_co], ObservableCollection[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S_co] | ClearAction[_S_co] | ReverseAction[_S_co] | ElementsChangedAction[_S_co]]: ...

    @abstractmethod
    def map(self, transformer: Callable[[_S_co], _T]) -> ObservableSequence[_T]: ...

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return NotImplemented
        if len(self) != len(other):
            return False
        return all(a == b for a, b in zip(self, other))


class IndexObservableSequence(ObservableSequence[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S_co] | ClearAction[_S_co] | ReverseAction[_S_co]]: ...

    @property
    @abstractmethod
    def delta_observable(self) -> ValuesObservable[AtIndexDeltaAction[_S_co]]: ...

    def map(self, transformer: Callable[[_S_co], _T]) -> IndexObservableSequence[_T]:
        return MappedIndexObservableSequence(self, transformer)


class ValueSequence(IndexObservableSequence[Value[_S]], ValueCollection[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def on_value_change(self) -> ValueObservable[AtIndicesDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S] | ElementsChangedAction[_S]]: ...

    @property
    @abstractmethod
    def value_delta_observable(self) -> ValuesObservable[DeltaAction[_S]]: ...

    @cached_property
    def unboxed(self) -> ObservableSequence[_S]:
        return UnboxedValueSequence(self)

    def as_raw_list(self) -> list[_S]:
        return [value.value for value in self]

    def __str__(self):
        return "[" + ", ".join(str(value) for value in self) + "]"


class UnboxedValueSequence(ObservableSequence[_S_co], Generic[_S_co]):
    def __init__(self, value_sequence: ValueSequence[_S_co]):
        self._value_sequence = value_sequence
        self._on_change = value_sequence.on_value_change
        self._delta_observable = value_sequence.value_delta_observable

    @overload
    def __getitem__(self, index: int) -> _S_co: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_S_co]: ...

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [value.value for value in self._value_sequence[index]]
        return self._value_sequence[index].value

    def __iter__(self):
        return self._value_sequence.value_iter()

    @property
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S_co] | ClearAction[_S_co] | ReverseAction[_S_co] | ElementsChangedAction[_S_co]]:
        return self._on_change

    @property
    def delta_observable(self) -> ValuesObservable[DeltaAction[_S_co]]:
        return self._delta_observable

    @property
    def length_value(self) -> IntValue:
        return self._value_sequence.length_value

    def map(self, transformer: Callable[[_S_co], _T]) -> ObservableSequence[_T]:
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"

    def __str__(self):
        return str(self._value_sequence)


class MutableObservableSequence(ObservableSequence[_S], MutableSequence[_S], Generic[_S], ABC):
    pass


class MutableIndexObservableSequence(IndexObservableSequence[_S], MutableSequence[_S], Generic[_S], ABC):
    pass


class MutableValueSequence(MutableObservableSequence[Value[_S]], Generic[_S], ABC):
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
    def pop(self, index: SupportsIndex = -1) -> Value[_S]: ...

    @overload
    @abstractmethod
    def __setitem__(self, key: int, value: _S | Value[_S]): ...

    @overload
    @abstractmethod
    def __setitem__(self, key: slice, value: Iterable[_S | Value[_S]]): ...

    @abstractmethod
    def __setitem__(self, key, value): ...


class ValueChangedMultipleTimesAction(ElementsChangedAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def new_item(self) -> _S_co: ...

    @property
    @abstractmethod
    def old_item(self) -> _S_co: ...

    @property
    @abstractmethod
    def count(self) -> int: ...

    @property
    def changes(self) -> Iterable[OneElementChangedAction[_S_co]]:
        return (SimpleOneElementChangedAction(new_item=self.new_item, old_item=self.old_item),) * self.count

    @property
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        remove_action = SimpleRemoveOneAction(item=self.old_item)
        add_action = SimpleAddOneAction(item=self.new_item)
        return (remove_action, add_action) * self.count

    def map(self, transformer: Callable[[_S_co], _T]) -> ValueChangedMultipleTimesAction[_T]:
        return SimpleValueChangedMultipleTimesAction(new_item=transformer(self.new_item), old_item=transformer(self.old_item), count=self.count)


class SimpleValueChangedMultipleTimesAction(ValueChangedMultipleTimesAction[_S_co], Generic[_S_co]):
    def __init__(self, new_item: _S_co, old_item: _S_co, count: int = 1):
        self._new_item = new_item
        self._old_item = old_item
        self._count = count

    @property
    def new_item(self) -> _S_co:
        return self._new_item

    @property
    def old_item(self) -> _S_co:
        return self._old_item

    @property
    def count(self) -> int:
        return self._count

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimpleValueChangedMultipleTimesAction):
            return NotImplemented
        return (self.new_item == other.new_item and
                self.old_item == other.old_item and
                self.count == other.count)

    def __repr__(self):
        return f"{self.__class__.__name__}(new_item={self.new_item!r}, old_item={self.old_item!r}, count={self.count})"


class IndexObservableSequenceBase(IndexObservableSequence[_S], Generic[_S]):
    def __init__(self, iterable: Iterable[_S] = ()):
        self._values = list(iterable)
        self._action_event = ValueEvent[AtIndicesDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]()
        self._deltas_event = ValueEvent[AtIndicesDeltasAction[_S]]()
        self._delta_observable = self._deltas_event.map_to_many(
            transformer=lambda deltas_action: deltas_action.delta_actions
        )
        self._len_value = IntVariable(len(self._values))

    @property
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]:
        return self._action_event

    @property
    def delta_observable(self) -> ValuesObservable[AtIndexDeltaAction[_S]]:
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
                self._deltas_event(action)
        else:
            self._len_value.value = new_length

    def is_observed(self):
        return self._action_event.is_observed() or self._deltas_event.is_observed()

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
                self._deltas_event(action)
        else:
            self._len_value.value = new_length

    def _insert(self, index: SupportsIndex, item: _S):
        self._values.insert(index, item)
        if self.is_observed():
            with self._len_value.set_delay_notify(len(self._values)):
                action = SimpleInsertAction(index.__index__(), item)
                self._action_event(action)
                self._deltas_event(action)
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
                self._deltas_event(action)
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
                self._deltas_event(action)
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
                self._deltas_event(action)
        else:
            self._len_value.value = len(self._values)

    def _remove_all(self, items: Iterable[_S]):
        indices_to_remove = list(self.indices_of(items))
        self._del_all(indices_to_remove)

    def _clear(self):
        if self._deltas_event.is_observed():
            removed_elements_with_index = tuple((enumerate(self)))
        else:
            removed_elements_with_index = None
        self._values.clear()

        with self._len_value.set_delay_notify(0):
            if removed_elements_with_index is not None:
                self._deltas_event(SimpleRemoveAtIndicesAction(removed_elements_with_index))
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
        action: AtIndicesDeltasAction[_S] | None = None
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
                self._deltas_event(action)
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
        self._deltas_event(action)

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
        if self._deltas_event.is_observed():
            remove_actions = (SimpleRemoveAtIndexAction(0, value) for value in self._values)
            added_actions = (SimpleInsertAction(index, value) for index, value in enumerate(self._values.__reversed__()))
            deltas_action = SimpleAtIndicesDeltasAction(tuple((*remove_actions, *added_actions)))
        else:
            deltas_action = None
        self._values.reverse()
        if self.is_observed():
            self._action_event(reverse_action())
            if deltas_action is not None:
                self._deltas_event(deltas_action)

    @property
    def length_value(self) -> IntValue:
        return self._len_value

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._values!r})"


class _ValueCell(Generic[_S]):
    def __init__(self, value: Value[_S], event: ValueEvent[ValueChangedMultipleTimesAction[_S]]):
        self._value = value
        self._count = 0
        self._action_event = event

    def on_added(self):
        self._count += 1
        if self._count == 1:
            self._value.observe(self._on_value_changed)

    def on_removed(self):
        self._count -= 1
        if self._count == 0:
            self._value.unobserve(self._on_value_changed)

    @property
    def count(self) -> int:
        return self._count

    def _on_value_changed(self, new_value: _S, old_value: _S):
        self._action_event.emit_lazy(lambda: SimpleValueChangedMultipleTimesAction(new_item=new_value, old_item=old_value, count=self.count))


class ValueSequenceBase(ValueSequence[_S], IndexObservableSequenceBase[Value[_S]], Generic[_S], ABC):
    _on_value_action: ValueObservable[AtIndicesDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S]]
    _on_value_delta_action: ValuesObservable[DeltaAction[_S]]
    _final_on_value_delta_action: ValuesObservable[DeltaAction[_S]]

    _cells: dict[Value[_S], _ValueCell[_S]]

    def __init__(self, iterable: Iterable[Value[_S]] = ()):
        super().__init__(iterable)
        self._cells = {}

        self._on_value_action = self.on_change.map(lambda action: action.map(lambda item: item.value))
        self._on_value_changed_event = ValueEvent[ValueChangedMultipleTimesAction[_S]]()
        self._final_on_value_action = self._on_value_action.or_value(self._on_value_changed_event)

        self._on_value_delta_action = self.delta_observable.map(lambda action: action.map(lambda item: item.value))
        self._on_value_delta_action_event = self._on_value_changed_event.map_to_many(
            transformer=lambda deltas_action: deltas_action.delta_actions
        )
        self._final_on_value_delta_action = self._on_value_delta_action.or_values(self._on_value_delta_action_event)
        self.delta_observable.observe_single(self._on_value_sequence_delta)

        for value in self:
            self._on_value_added(value)

    @property
    def on_value_change(self) -> ValueObservable[AtIndicesDeltasAction[_S] | ClearAction[_S] | ReverseAction[_S] | ElementsChangedAction[_S]]:
        return self._final_on_value_action

    @property
    def value_delta_observable(self) -> ValuesObservable[DeltaAction[_S]]:
        return self._final_on_value_delta_action

    def _on_value_sequence_delta(self, action: DeltaAction[Value[_S]]):
        if action.is_add:
            self._on_value_added(action.value)
        else:
            self._on_value_removed(action.value)

    def _on_value_added(self, value: Value[_S]):
        try:
            _ = value.constant_value_or_raise
            return
        except NotConstantError:
            pass
        try:
            cell = self._cells[value]
        except KeyError:
            cell = _ValueCell(value, self._on_value_changed_event)
            self._cells[value] = cell
        cell.on_added()

    def _on_value_removed(self, value: Value[_S]):
        try:
            _ = value.constant_value_or_raise
            return
        except NotConstantError:
            pass
        cell = self._cells[value]
        cell.on_removed()
        if cell.count == 0:
            del self._cells[value]


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


class ValueList(ValueSequenceBase[_S], MutableIndexObservableSequence[Value[_S]], Generic[_S], ABC):
    def append(self, item: Value[_S]):
        self._append(item)

    def extend(self, items: Iterable[Value[_S]]):
        self._extend(items)

    def insert(self, index: SupportsIndex, item: Value[_S]):
        self._insert(index, item)

    def insert_all(self, items_with_index: Iterable[tuple[int, Value[_S]]]):
        self._insert_all(items_with_index)

    def remove(self, item: Value[_S]):
        self._remove(item)

    def __delitem__(self, key: SupportsIndex | slice):
        self._delitem(key)

    def del_all(self, indices: Iterable[SupportsIndex]):
        self._del_all(indices)

    def remove_all(self, items: Iterable[Value[_S]]):
        self._remove_all(items)

    def clear(self):
        self._clear()

    def pop(self, index: SupportsIndex = -1) -> Value[_S]:
        return self._pop(index)

    @overload
    def __setitem__(self, key: SupportsIndex, value: Value[_S]): ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[Value[_S]]): ...

    def __setitem__(self, key, value):
        self._setitem(key, value)

    def __iadd__(self, values: Iterable[Value[_S]]) -> Self:  # type: ignore[override, misc]
        return self._iadd(values)

    def __imul__(self, value: SupportsIndex) -> Self:
        return self._imul(value)

    def __mul__(self, other: SupportsIndex) -> MutableSequence[Value[_S]]:
        return self._mul(other)

    def reverse(self):
        self._reverse()


def _to_value(value: _S | Value[_S],
              checker: Callable[[Any], TypeIs[_S]],
              constant_factory: Callable[[_S], Constant[_S]]) -> Value[_S]:
    if checker(value):
        return constant_factory(value)
    else:
        return value


def _to_values(values: Iterable[_S | Value[_S]],
               checker: Callable[[Any], TypeIs[_S]],
               constant_factory: Callable[[_S], Constant[_S]]) -> Iterable[Value[_S]]:
    return (_to_value(value, checker, constant_factory) for value in values)


def _with_indices_to_values_with_indices(values_with_indices: Iterable[tuple[int, _S | Value[_S]]],
                                         checker: Callable[[Any], TypeIs[_S]],
                                         constant_factory: Callable[[_S], Constant[_S]]) -> Iterable[tuple[int, Value[_S]]]:
    return ((index, _to_value(value, checker, constant_factory)) for index, value in values_with_indices)


class TypedValueList(ValueList[_S], Generic[_S]):
    def __init__(self, values: Iterable[_S | Value[_S]] | None = None, *,
                 checker: Callable[[Any], TypeIs[_S]],
                 constant_factory: Callable[[_S], Constant[_S]] = Constant.of):
        if values is None:
            values = ()
        self._checker = checker
        self._constant_factory = constant_factory
        super().__init__(_to_values(values, checker, constant_factory))

    def append(self, item: _S | Value[_S]):
        super().append(_to_value(item, self._checker, self._constant_factory))

    def extend(self, items: Iterable[_S | Value[_S]]):
        super().extend(_to_values(items, self._checker, self._constant_factory))

    def __iadd__(self, values: Iterable[_S | Value[_S]]) -> Self:
        super().__iadd__(_to_values(values, self._checker, self._constant_factory))
        return self

    def insert(self, index: SupportsIndex, item: _S | Value[_S]):
        super().insert(index, _to_value(item, self._checker, self._constant_factory))

    def insert_all(self, items_with_index: Iterable[tuple[int, _S | Value[_S]]]):
        super().insert_all(_with_indices_to_values_with_indices(items_with_index, self._checker, self._constant_factory))

    def remove(self, item: _S | Value[_S]):
        super().remove(_to_value(item, self._checker, self._constant_factory))

    def remove_all(self, items: Iterable[_S | Value[_S]]):
        super().remove_all(_to_values(items, self._checker, self._constant_factory))

    @overload
    def __setitem__(self, key: SupportsIndex, value: _S | Value[_S]): ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[_S | Value[_S]]): ...

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self._setitem_slice(key, _to_values(value, self._checker, self._constant_factory))
        else:
            self._setitem_index(key, _to_value(value, self._checker, self._constant_factory))

    def _compare_value(self, self_value: Value[int], other_value: Value[int] | int) -> bool:
        if self_value == other_value:
            return True
        if self._checker(other_value):
            try:
                return self_value.constant_value_or_raise == other_value
            except NotConstantError:
                return False
        if isinstance(other_value, Value):
            return False
        return False

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return NotImplemented
        if len(self) != len(other):
            return False
        for self_value, other_value in zip(self, other):
            if not self._compare_value(self_value, other_value):
                return False
        return True


class MappedIndexObservableSequence(IndexObservableSequenceBase[_S], Generic[_S]):
    def __init__(self, mapped_from: IndexObservableSequence[_T], map_func: Callable[[_T], _S]):
        super().__init__(map_func(item) for item in mapped_from)
        self._mapped_from = mapped_from
        self._map_func = map_func

        def on_action(other_action: AtIndicesDeltasAction[_T] | ClearAction[_T] | ReverseAction[_T]):
            if isinstance(other_action, AtIndicesDeltasAction):
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
                            self._deltas_event(action)
                    else:
                        self._len_value.value = len(self._values)
            elif isinstance(other_action, ClearAction):
                self._clear()
            elif isinstance(other_action, ReverseAction):
                self._reverse()

        mapped_from.on_change.observe(on_action)

    def _is_observed(self):
        return self._action_event.is_observed() or self._deltas_event.is_observed()

    @property
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S] | ClearAction | ReverseAction]:
        return self._action_event

    @property
    def delta_observable(self) -> ValuesObservable[AtIndexDeltaAction[_S]]:
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
    def on_change(self) -> ValueObservable[AtIndicesDeltasAction[_S] | ClearAction | ReverseAction]:
        return void_value_observable()

    @property
    def delta_observable(self) -> ValuesObservable[AtIndexDeltaAction[_S]]:
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
