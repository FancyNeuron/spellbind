from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from typing import Generic, SupportsIndex, Iterable, TypeVar, Callable

from typing_extensions import override

_S = TypeVar("_S")
_S_co = TypeVar("_S_co", covariant=True)
_T = TypeVar("_T")


class CollectionAction(Generic[_S_co], ABC):
    @property
    @abstractmethod
    def is_permutation_only(self) -> bool: ...

    @abstractmethod
    def map(self, transformer: Callable[[_S_co], _T]) -> CollectionAction[_T]: ...

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ClearAction(CollectionAction[_S_co], Generic[_S_co]):
    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> ClearAction[_T]:
        return clear_action()


class SingleValueAction(CollectionAction[_S_co], Generic[_S_co]):
    @property
    @abstractmethod
    def value(self) -> _S_co: ...


class DeltasAction(CollectionAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]: ...

    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> DeltasAction[_T]:
        mapped = tuple(action.map(transformer) for action in self.delta_actions)
        return SimpleDeltasAction(mapped)


class SimpleDeltasAction(DeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, delta_actions: tuple[DeltaAction[_S_co], ...]):
        self._delta_actions = delta_actions

    @property
    @override
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        return self._delta_actions


class DeltaAction(SingleValueAction[_S_co], DeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @property
    @abstractmethod
    def is_add(self) -> bool: ...

    @property
    @override
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        return (self,)

    @abstractmethod
    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> DeltaAction[_T]: ...


class AddOneAction(DeltaAction[_S_co], Generic[_S_co], ABC):
    @property
    @override
    def is_add(self) -> bool:
        return True

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> AddOneAction[_T]:
        return SimpleAddOneAction(transformer(self.value))

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"


class SimpleAddOneAction(AddOneAction[_S_co], Generic[_S_co]):
    def __init__(self, item: _S_co):
        self._item = item

    @property
    @override
    def value(self) -> _S_co:
        return self._item


class RemoveOneAction(DeltaAction[_S_co], Generic[_S_co], ABC):
    @property
    @override
    def is_add(self) -> bool:
        return False

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> RemoveOneAction[_T]:
        return SimpleRemoveOneAction(transformer(self.value))

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"


class SimpleRemoveOneAction(RemoveOneAction[_S_co], Generic[_S_co]):
    def __init__(self, item: _S_co):
        self._item = item

    @property
    @override
    def value(self) -> _S_co:
        return self._item


class ElementsChangedAction(DeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def changes(self) -> Iterable[OneElementChangedAction[_S_co]]: ...

    @property
    @override
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        return tuple(itertools.chain.from_iterable(
            (SimpleRemoveOneAction(change.old_item), SimpleAddOneAction(change.new_item))
            for change in self.changes
        ))

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> ElementsChangedAction[_T]:
        return SimpleElementsChangedAction(
            changes=tuple(change.map(transformer) for change in self.changes)
        )


class SimpleElementsChangedAction(ElementsChangedAction[_S_co], Generic[_S_co]):
    def __init__(self, changes: tuple[OneElementChangedAction[_S_co], ...]):
        self._changes = changes

    @property
    @override
    def changes(self) -> Iterable[OneElementChangedAction[_S_co]]:
        return self._changes

    @override
    def __eq__(self, other):
        if not isinstance(other, ElementsChangedAction):
            return NotImplemented
        return self.changes == other.changes

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(changes={self.changes})"


class OneElementChangedAction(DeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def new_item(self) -> _S_co: ...

    @property
    @abstractmethod
    def old_item(self) -> _S_co: ...

    @property
    @override
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        return SimpleRemoveOneAction(self.old_item), SimpleAddOneAction(self.new_item)

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> OneElementChangedAction[_T]:
        return SimpleOneElementChangedAction(new_item=transformer(self.new_item), old_item=transformer(self.old_item))


class SimpleOneElementChangedAction(OneElementChangedAction[_S_co], Generic[_S_co]):
    def __init__(self, *, new_item: _S_co, old_item: _S_co):
        self._new_item = new_item
        self._old_item = old_item

    @property
    @override
    def new_item(self) -> _S_co:
        return self._new_item

    @property
    @override
    def old_item(self) -> _S_co:
        return self._old_item

    @override
    def __eq__(self, other):
        if not isinstance(other, OneElementChangedAction):
            return NotImplemented
        return (self.new_item == other.new_item and
                self.old_item == other.old_item)

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(new_item={self.new_item}, old_item={self.old_item})"


CLEAR_ACTION: ClearAction = ClearAction()


def clear_action() -> ClearAction[_S_co]:
    return CLEAR_ACTION  # type: ignore[return-value]


class SequenceAction(CollectionAction[_S_co], Generic[_S_co], ABC):
    pass


class SequenceValueChangedAction(SingleValueAction[_S_co], SequenceAction[_S_co], Generic[_S_co], ABC):
    pass


class AtIndexAction(SequenceAction[_S_co], Generic[_S_co]):
    @property
    @abstractmethod
    def index(self) -> int: ...

    @property
    @override
    def is_permutation_only(self) -> bool:
        return False


class AtIndicesDeltasAction(SequenceAction[_S_co], DeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]: ...

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> AtIndicesDeltasAction[_T]:
        mapped = tuple(action.map(transformer) for action in self.delta_actions)
        return SimpleAtIndicesDeltasAction(mapped)


class AtIndexDeltaAction(AtIndexAction[_S_co], DeltaAction[_S_co], AtIndicesDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return (self,)

    @abstractmethod
    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> AtIndexDeltaAction[_T]: ...

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index}, value={self.value})"


class InsertAction(AtIndexDeltaAction[_S_co], AddOneAction[_S_co], Generic[_S_co], ABC):
    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> InsertAction[_T]:
        return SimpleInsertAction(self.index, transformer(self.value))


class SimpleInsertAction(InsertAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, item: _S_co):
        self._index = index
        self._item = item

    @property
    @override
    def index(self) -> int:
        return self._index.__index__()

    @property
    @override
    def value(self) -> _S_co:
        return self._item

    @override
    def __eq__(self, other):
        if not isinstance(other, InsertAction):
            return NotImplemented
        return self.index == other.index and self.value == other.value


class InsertAllAction(AtIndicesDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def index_with_items(self) -> tuple[tuple[int, _S_co], ...]: ...

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(SimpleInsertAction(index + i, item) for i, (index, item) in enumerate(self.index_with_items))

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> InsertAllAction[_T]:
        return SimpleInsertAllAction(tuple((index, transformer(item)) for index, item in self.index_with_items))

    @override
    def __eq__(self, other):
        if not isinstance(other, InsertAllAction):
            return NotImplemented
        return self.index_with_items == other.index_with_items


class SimpleInsertAllAction(InsertAllAction[_S_co], Generic[_S_co]):
    def __init__(self, sorted_index_with_items: tuple[tuple[int, _S_co], ...]):
        self._index_with_items = sorted_index_with_items

    @property
    @override
    def index_with_items(self) -> tuple[tuple[int, _S_co], ...]:
        return self._index_with_items


class RemoveAtIndexAction(AtIndexDeltaAction[_S_co], RemoveOneAction[_S_co], Generic[_S_co], ABC):
    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> RemoveAtIndexAction[_T]:
        return SimpleRemoveAtIndexAction(self.index, transformer(self.value))

    @override
    def __eq__(self, other):
        if not isinstance(other, RemoveAtIndexAction):
            return NotImplemented
        return self.index == other.index and self.value == other.value


class SimpleRemoveAtIndexAction(RemoveAtIndexAction[_S_co], RemoveOneAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, item: _S_co):
        self._index = index.__index__()
        self._item = item

    @property
    @override
    def index(self) -> int:
        return self._index

    @property
    @override
    def value(self) -> _S_co:
        return self._item


class RemoveAtIndicesAction(AtIndicesDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def removed_elements_with_index(self) -> tuple[tuple[int, _S_co], ...]: ...

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> RemoveAtIndicesAction[_T]:
        return SimpleRemoveAtIndicesAction(tuple(
            (index, transformer(item))
            for index, item
            in self.removed_elements_with_index
        ))

    @override
    def __eq__(self, other):
        if not isinstance(other, RemoveAtIndicesAction):
            return NotImplemented
        return self.removed_elements_with_index == other.removed_elements_with_index

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}({self.removed_elements_with_index})"


class SimpleRemoveAtIndicesAction(RemoveAtIndicesAction[_S_co], Generic[_S_co]):
    def __init__(self, removed_elements_with_index: tuple[tuple[int, _S_co], ...]):
        self._removed_elements_with_index = removed_elements_with_index

    @property
    @override
    def removed_elements_with_index(self) -> tuple[tuple[int, _S_co], ...]:
        return self._removed_elements_with_index

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(SimpleRemoveAtIndexAction(index - i, item) for i, (index, item) in enumerate(self._removed_elements_with_index))


class SimpleAtIndicesDeltasAction(AtIndicesDeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, delta_actions: tuple[AtIndexDeltaAction[_S_co], ...]):
        self._delta_actions = delta_actions

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return self._delta_actions


class SetAtIndexAction(AtIndexAction[_S_co], AtIndicesDeltasAction[_S_co], OneElementChangedAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    @override
    def index(self) -> int: ...

    @property
    @abstractmethod
    @override
    def new_item(self) -> _S_co: ...

    @property
    @abstractmethod
    @override
    def old_item(self) -> _S_co: ...

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return (SimpleRemoveAtIndexAction(self.index, self.old_item),
                SimpleInsertAction(self.index, self.new_item))

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> SetAtIndexAction[_T]:
        return SimpleSetAtIndexAction(self.index, old_item=transformer(self.old_item), new_item=transformer(self.new_item))

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index}, old_item={self.old_item}, new_item={self.new_item})"

    @override
    def __eq__(self, other):
        if not isinstance(other, SetAtIndexAction):
            return NotImplemented
        return (self.index == other.index and
                self.old_item == other.old_item and
                self.new_item == other.new_item)


class SimpleSetAtIndexAction(SetAtIndexAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, *, new_item: _S_co, old_item: _S_co):
        self._index = index.__index__()
        self._new_item = new_item
        self._old_item = old_item

    @property
    @override
    def index(self) -> int:
        return self._index

    @property
    @override
    def new_item(self) -> _S_co:
        return self._new_item

    @property
    @override
    def old_item(self) -> _S_co:
        return self._old_item


class SliceSetAction(AtIndicesDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def indices(self) -> tuple[int, ...]: ...

    @property
    @abstractmethod
    def new_items(self) -> tuple[_S_co, ...]: ...

    @property
    @abstractmethod
    def old_items(self) -> tuple[_S_co, ...]: ...

    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> SliceSetAction[_T]:
        return SimpleSliceSetAction(indices=self.indices,
                                    new_items=tuple(transformer(item) for item in self.new_items),
                                    old_items=tuple(transformer(item) for item in self.old_items))

    @override
    def __eq__(self, other):
        if not isinstance(other, SliceSetAction):
            return NotImplemented
        return (self.indices == other.indices and
                self.new_items == other.new_items and
                self.old_items == other.old_items)

    @override
    def __repr__(self):
        return (f"{self.__class__.__name__}(indices={self.indices}, "
                f"new_items={self.new_items}, old_items={self.old_items})")


class SimpleSliceSetAction(SliceSetAction[_S_co], Generic[_S_co]):
    def __init__(self, *, indices: tuple[int, ...], new_items: tuple[_S_co, ...], old_items: tuple[_S_co, ...]):
        self._indices = indices
        self._new_items = new_items
        self._old_items = old_items

    @property
    @override
    def indices(self) -> tuple[int, ...]:
        return self._indices

    @property
    @override
    def new_items(self) -> tuple[_S_co, ...]:
        return self._new_items

    @property
    @override
    def old_items(self) -> tuple[_S_co, ...]:
        return self._old_items

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(itertools.chain(self._remove_delta_actions, self._insert_delta_actions))

    @property
    def _remove_delta_actions(self) -> Iterable[AtIndexDeltaAction[_S_co]]:
        return (SimpleRemoveAtIndexAction(index - i, item) for i, (index, item) in enumerate(zip(self._indices, self._old_items)))

    @property
    def _insert_delta_actions(self) -> Iterable[AtIndexDeltaAction[_S_co]]:
        first_index = self._indices[0]
        return (SimpleInsertAction(first_index + i, item) for i, item in enumerate(self._new_items))


class SetAtIndicesAction(AtIndicesDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def indices_with_new_and_old_items(self) -> tuple[tuple[int, _S_co, _S_co], ...]: ...

    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(itertools.chain.from_iterable(
            (SimpleRemoveAtIndexAction(index, old), SimpleInsertAction(index, new))
            for index, new, old in self.indices_with_new_and_old_items))

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> SetAtIndicesAction[_T]:
        return SimpleSetAtIndicesAction(tuple((index, transformer(new), transformer(old))
                                              for index, new, old
                                              in self.indices_with_new_and_old_items))

    @override
    def __eq__(self, other):
        if not isinstance(other, SetAtIndicesAction):
            return NotImplemented
        return self.indices_with_new_and_old_items == other.indices_with_new_and_old_items

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(indices_with_new_and_old_items={self.indices_with_new_and_old_items})"


class SimpleSetAtIndicesAction(SetAtIndicesAction[_S_co], Generic[_S_co]):
    def __init__(self, indices_with_new_and_old: tuple[tuple[int, _S_co, _S_co], ...]):
        self._index_with_new_and_old_items = indices_with_new_and_old

    @property
    @override
    def indices_with_new_and_old_items(self) -> tuple[tuple[int, _S_co, _S_co], ...]:
        return self._index_with_new_and_old_items

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(itertools.chain.from_iterable(
            (SimpleRemoveAtIndexAction(index, old), SimpleInsertAction(index, new))
            for index, new, old in self._index_with_new_and_old_items))


class ReverseAction(SequenceAction[_S_co], Generic[_S_co]):
    @property
    @override
    def is_permutation_only(self) -> bool:
        return True

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> ReverseAction[_T]:
        return reverse_action()


class ExtendAction(AtIndicesDeltasAction[_S_co], SequenceAction[_S_co], Generic[_S_co], ABC):
    @property
    @override
    def is_permutation_only(self) -> bool:
        return False

    @property
    @abstractmethod
    def items(self) -> Iterable[_S_co]: ...

    @property
    @abstractmethod
    def old_sequence_length(self) -> int: ...

    @property
    @override
    def delta_actions(self) -> tuple[AtIndexDeltaAction[_S_co], ...]:
        return tuple(SimpleInsertAction(i, item) for i, item in enumerate(self.items, start=self.old_sequence_length))

    @override
    def map(self, transformer: Callable[[_S_co], _T]) -> ExtendAction[_T]:
        return SimpleExtendAction(self.old_sequence_length, tuple(transformer(item) for item in self.items))

    @override
    def __eq__(self, other):
        if not isinstance(other, ExtendAction):
            return NotImplemented
        return (self.old_sequence_length == other.old_sequence_length and
                tuple(self.items) == tuple(other.items))

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}(old_sequence_length={self.old_sequence_length}, items={self.items})"


class SimpleExtendAction(ExtendAction[_S_co], Generic[_S_co]):
    def __init__(self, old_sequence_length: int, extend_by: tuple[_S_co, ...]):
        self._old_sequence_length = old_sequence_length
        self._items = extend_by

    @property
    @override
    def items(self) -> Iterable[_S_co]:
        return self._items

    @property
    @override
    def old_sequence_length(self) -> int:
        return self._old_sequence_length


REVERSE_SEQUENCE_ACTION: ReverseAction = ReverseAction()


def reverse_action() -> ReverseAction[_S_co]:
    return REVERSE_SEQUENCE_ACTION  # type: ignore[return-value]
