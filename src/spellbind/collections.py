from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable, Collection, Sequence, Iterable, SupportsIndex, Iterator, Any, \
    overload

from typing_extensions import Self

from spellbind import int_values
from spellbind.event import ValuesEvent
from spellbind.int_values import IntVariable, IntValue
from spellbind.observables import ValuesObservable, void_values_observable

_S = TypeVar("_S")
_T = TypeVar("_T")


class ObservableCollection(Collection[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def added_observable(self) -> ValuesObservable[_S]: ...

    @property
    @abstractmethod
    def removed_observable(self) -> ValuesObservable[_S]: ...

    @property
    @abstractmethod
    def length_value(self) -> IntValue: ...

    def __len__(self) -> int:
        return self.length_value.value


class ObservableSequence(Sequence[_S], ObservableCollection[_S], Generic[_S], ABC):
    @property
    @abstractmethod
    def added_index_observable(self) -> ValuesObservable[tuple[int, _S]]: ...

    @property
    @abstractmethod
    def removed_index_observable(self) -> ValuesObservable[tuple[int, _S]]: ...


class ObservableMutableSequence(ObservableSequence[_S], Generic[_S], ABC):
    pass


class ObservableList(ObservableMutableSequence[_S], Generic[_S]):
    def __init__(self, iterable: Iterable[_S] = ()):
        self._values = list(iterable)
        self._index_added_event = ValuesEvent[tuple[int, _S]]()
        self._added_event = self._index_added_event.derive(lambda v: v[1])
        self._index_removed_event = ValuesEvent[tuple[int, _S]]()
        self._removed_event = self._index_removed_event.derive(lambda v: v[1])
        self._len_value = IntVariable(len(self._values))

    @property
    def added_observable(self) -> ValuesObservable[_S]:
        return self._added_event

    @property
    def added_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return self._index_added_event

    @property
    def removed_observable(self) -> ValuesObservable[_S]:
        return self._removed_event

    @property
    def removed_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return self._index_removed_event

    @overload
    def __getitem__(self, index: SupportsIndex) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_S]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> _S | Sequence[_S]:
        return self._values[index]

    def append(self, item: _S):
        self._values.append(item)
        new_length = len(self._values)
        with self._len_value.set_delay_notify(new_length):
            self._index_added_event.emit_single((new_length - 1, item))

    def extend(self, items: Iterable[_S]):
        old_length = len(self._values)
        self._values.extend(items)
        new_length = len(self._values)
        if old_length == new_length:
            return
        with self._len_value.set_delay_notify(new_length):
            self._index_added_event(tuple(enumerate(items, start=old_length)))

    def insert(self, index: SupportsIndex, item: _S):
        self._values.insert(index, item)
        with self._len_value.set_delay_notify(len(self._values)):
            index = index.__index__()
            self._index_added_event.emit_single((index, item))

    def insert_all(self, index_with_items: Iterable[tuple[int, _S]]):
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
            self._index_added_event(sorted_index_with_items)

    def remove(self, item: _S):
        index = self.index(item)
        del self[index]

    def __delitem__(self, key: SupportsIndex | slice):
        if isinstance(key, slice):
            self._delitem_slice(key)
        else:
            self._delitem_index(key)

    def _delitem_index(self, key: SupportsIndex):
        index = key.__index__()
        item = self[index]
        self._values.__delitem__(index)
        with self._len_value.set_delay_notify(len(self._values)):
            self._index_removed_event.emit_single((index, item))

    def _delitem_slice(self, slice_key: slice):
        indices = range(*slice_key.indices(len(self._values)))
        if not indices:
            return
        self.del_all(indices)

    def indices_of(self, items: Iterable[_S]) -> Iterable[int]:
        last_indices: dict[_S, int] = {}
        for item in items:
            last_index = last_indices.get(item, 0)
            index = self.index(item, last_index)
            last_indices[item] = index + 1
            yield index

    def del_all(self, indices: Iterable[SupportsIndex]):
        indices_ints: tuple[int, ...] = tuple(index.__index__() for index in indices)
        if len(indices_ints) == 0:
            return

        reverse_sorted_indices = sorted(indices_ints, reverse=True)
        reverse_elements_with_index: tuple[tuple[int, _S], ...] = tuple((i, self._values.pop(i)) for i in reverse_sorted_indices)
        removed_elements_with_index: tuple[tuple[int, _S], ...] = tuple(reversed(reverse_elements_with_index))
        with self._len_value.set_delay_notify(len(self._values)):
            self._index_removed_event(removed_elements_with_index)

    def remove_all(self, items: Iterable[_S]):
        indices_to_remove = list(self.indices_of(items))
        self.del_all(indices_to_remove)

    def clear(self):
        removed_elements_with_index = tuple((enumerate(self)))

        self._values.clear()

        with self._len_value.set_delay_notify(0):
            self._index_removed_event(removed_elements_with_index)

    def pop(self, index: SupportsIndex = -1) -> _S:
        index = index.__index__()
        if index < 0:
            index += len(self._values)
        item = self[index]
        del self[index]
        return item

    @overload
    def __setitem__(self, key: SupportsIndex, value: _S): ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[_S]): ...

    def __setitem__(self, key, value):
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
        self._index_removed_event.emit_single((index, old_value))
        self._index_added_event.emit_single((index, value))

    def __iadd__(self, values: Iterable[_S]) -> Self:  # type: ignore[override, misc]
        self.extend(values)
        return self

    def __imul__(self, value: SupportsIndex) -> Self:
        mul = value.__index__()
        if mul == 0:
            self.clear()
            return self
        elif mul == 1:
            return self
        extend_by = tuple(self._values.__mul__(mul - 1))
        self.extend(extend_by)
        return self

    def reverse(self):
        removed_elements_with_index = tuple(enumerate(self))
        added_elements_with_index = tuple(enumerate(self._values.__reversed__()))
        self._values.clear()
        self._values.extend(item for _, item in added_elements_with_index)
        with self._len_value.set_delay_notify(len(self._values)):
            self._index_removed_event(removed_elements_with_index)
            self._index_added_event(added_elements_with_index)

    def map(self, transformer: Callable[[_S], _T]) -> ObservableSequence[_T]:
        return MappedObservableSequence(self, transformer)

    @property
    def length_value(self) -> IntVariable:
        return self._len_value

    def __str__(self):
        return self._values.__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._values!r})"


class MappedObservableSequence(ObservableSequence[_S], Generic[_S]):
    def __init__(self, mapped_from: ObservableSequence[_T], map_func: Callable[[_T], _S]):
        self._mapped_from = mapped_from
        self._map_func = map_func
        self._values = [map_func(item) for item in mapped_from]
        self._index_added_event = ValuesEvent[tuple[int, _S]]()
        self._added_event = self._index_added_event.derive(lambda v: v[1])
        self._index_removed_event = ValuesEvent[tuple[int, _S]]()
        self._removed_event = self._index_removed_event.derive(lambda v: v[1])
        self._len_value = IntVariable(len(mapped_from))

        mapped_from.added_index_observable.weak_observe(self._on_batch_added)
        mapped_from.removed_index_observable.weak_observe(self._on_batch_removed)

    def _on_batch_added(self, batch: Iterable[tuple[int, Any]]):
        transformed: tuple[tuple[int, _S], ...] = tuple((index, self._map_func(item)) for index, item in batch)

        for index, item in reversed(transformed):
            self._values.insert(index, item)
        with self._len_value.set_delay_notify(len(self._values)):
            self._index_added_event(transformed)

    def _on_batch_removed(self, batch: Iterable[tuple[int, Any]]):
        transformed: tuple[tuple[int, _S], ...] = tuple((index, self._map_func(item)) for index, item in batch)
        for index, item in reversed(transformed):
            del self._values[index]

        with self._len_value.set_delay_notify(len(self._values)):
            self._index_removed_event(transformed)

    @property
    def added_observable(self) -> ValuesObservable[_S]:
        return self._added_event

    @property
    def added_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return self._index_added_event

    @property
    def removed_observable(self) -> ValuesObservable[_S]:
        return self._removed_event

    @property
    def removed_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return self._index_removed_event

    @property
    def length_value(self) -> IntValue:
        return self._len_value

    def __iter__(self) -> Iterator[_S]:
        return iter(self._values)

    @overload
    def __getitem__(self, index: int) -> _S: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_S]: ...

    def __getitem__(self, index):
        return self._values[index]


class _EmptyObservableSequence(ObservableSequence[_S], Generic[_S]):
    @property
    def length_value(self) -> IntValue:
        return int_values.ZERO

    @property
    def added_observable(self) -> ValuesObservable[_S]:
        return void_values_observable()

    @property
    def added_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return void_values_observable()

    @property
    def removed_observable(self) -> ValuesObservable[_S]:
        return void_values_observable()

    @property
    def removed_index_observable(self) -> ValuesObservable[tuple[int, _S]]:
        return void_values_observable()

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
