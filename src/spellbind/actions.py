from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, SupportsIndex, Iterable, TypeVar, Callable

_S = TypeVar("_S")
_S_co = TypeVar("_S_co", covariant=True)
_T = TypeVar("_T")


class CollectionAction(Generic[_S_co], ABC):
    @property
    @abstractmethod
    def is_permutation_only(self) -> bool: ...


class ClearAction(CollectionAction[_S_co], Generic[_S_co]):
    @property
    def is_permutation_only(self) -> bool:
        return False


class SingleValueAction(CollectionAction[_S_co], Generic[_S_co]):
    @property
    @abstractmethod
    def value(self) -> _S_co: ...


class DeltaAction(SingleValueAction[_S_co], Generic[_S_co], ABC):
    @property
    def is_permutation_only(self) -> bool:
        return False

    @property
    @abstractmethod
    def is_add(self) -> bool: ...


class DeltasAction(CollectionAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]: ...

    @property
    def is_permutation_only(self) -> bool:
        return False


class SimpleDeltasAction(DeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, delta_actions: tuple[DeltaAction[_S_co], ...]):
        self._delta_actions = delta_actions

    @property
    def delta_actions(self) -> tuple[DeltaAction[_S_co], ...]:
        return self._delta_actions


class AddOneAction(DeltaAction[_S_co], Generic[_S_co], ABC):
    @property
    def is_add(self) -> bool:
        return True


class SimpleAddOneAction(AddOneAction[_S_co], Generic[_S_co]):
    def __init__(self, item: _S_co):
        self._item = item

    @property
    def value(self) -> _S_co:
        return self._item


class RemoveOneAction(DeltaAction[_S_co], Generic[_S_co], ABC):
    @property
    def is_add(self) -> bool:
        return False


class SimpleRemoveOneAction(RemoveOneAction[_S_co], Generic[_S_co]):
    def __init__(self, item: _S_co):
        self._item = item

    @property
    def value(self) -> _S_co:
        return self._item


CLEAR_ACTION: ClearAction = ClearAction()


def clear_action() -> ClearAction[_S_co]:
    return CLEAR_ACTION  # type: ignore[return-value]


class SequenceAction(CollectionAction[_S_co], Generic[_S_co], ABC):
    pass


class AtIndexAction(SequenceAction[_S_co], Generic[_S_co]):
    @property
    @abstractmethod
    def index(self) -> int: ...

    @property
    def is_permutation_only(self) -> bool:
        return False


class SequenceDeltasAction(SequenceAction[_S_co], DeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    @abstractmethod
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]: ...

    def map(self, transformer: Callable[[_S_co], _T]) -> SequenceDeltasAction[_T]:
        mapped = tuple(action.map(transformer) for action in self.delta_actions)
        return SimpleSequenceDeltasAction(mapped)


class SequenceDeltaAction(AtIndexAction[_S_co], DeltaAction[_S_co], SequenceDeltasAction[_S_co], Generic[_S_co], ABC):
    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return (self,)

    @abstractmethod
    def map(self, transformer: Callable[[_S_co], _T]) -> SequenceDeltaAction[_T]: ...

    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index}, value={self.value})"


class InsertAction(SequenceDeltaAction[_S_co], AddOneAction[_S_co], Generic[_S_co], ABC):
    def map(self, transformer: Callable[[_S_co], _T]) -> InsertAction[_T]:
        return SimpleInsertAction(self.index, transformer(self.value))


class SimpleInsertAction(InsertAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, item: _S_co):
        self._index = index
        self._item = item

    @property
    def index(self) -> int:
        return self._index.__index__()

    @property
    def value(self) -> _S_co:
        return self._item


class InsertAllAction(SequenceDeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, sorted_index_with_items: tuple[tuple[int, _S_co], ...]):
        self._index_with_items = sorted_index_with_items

    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return tuple(SimpleInsertAction(index + i, item) for i, (index, item) in enumerate(self._index_with_items))

    def map(self, transformer: Callable[[_S_co], _T]) -> InsertAllAction[_T]:
        return InsertAllAction(tuple((index, transformer(item)) for index, item in self._index_with_items))


class RemoveAtIndexAction(SequenceDeltaAction[_S_co], RemoveOneAction[_S_co], Generic[_S_co], ABC):
    def map(self, transformer: Callable[[_S_co], _T]) -> RemoveAtIndexAction[_T]:
        return SimpleRemoveAtIndexAction(self.index, transformer(self.value))


class SimpleRemoveAtIndexAction(RemoveAtIndexAction[_S_co], RemoveOneAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, item: _S_co):
        self._index = index.__index__()
        self._item = item

    @property
    def index(self) -> int:
        return self._index

    @property
    def value(self) -> _S_co:
        return self._item


class RemoveAtIndicesAction(SequenceDeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, removed_elements_with_index: tuple[tuple[int, _S_co], ...]):
        self._removed_elements_with_index = removed_elements_with_index

    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return tuple(SimpleRemoveAtIndexAction(index - i, item) for i, (index, item) in enumerate(self._removed_elements_with_index))

    def map(self, transformer: Callable[[_S_co], _T]) -> RemoveAtIndicesAction[_T]:
        return RemoveAtIndicesAction(tuple((index, transformer(item)) for index, item in self._removed_elements_with_index))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._removed_elements_with_index})"


class SimpleSequenceDeltasAction(SequenceDeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, delta_actions: tuple[SequenceDeltaAction[_S_co], ...]):
        self._delta_actions = delta_actions

    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return self._delta_actions


class SetAtIndexAction(AtIndexAction[_S_co], SequenceDeltasAction[_S_co], Generic[_S_co]):
    def __init__(self, index: SupportsIndex, old_item: _S_co, new_item: _S_co):
        self._index = index.__index__()
        self._old_item = old_item
        self._new_item = new_item

    @property
    def index(self) -> int:
        return self._index

    @property
    def old_item(self) -> _S_co:
        return self._old_item

    @property
    def new_item(self) -> _S_co:
        return self._new_item

    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return (SimpleRemoveAtIndexAction(self._index, self._old_item),
                SimpleInsertAction(self._index, self._new_item))

    def __repr__(self):
        return f"{self.__class__.__name__}(index={self.index}, old_item={self.old_item}, new_item={self.new_item})"


class ReverseAction(SequenceAction[_S_co], Generic[_S_co]):
    @property
    def is_permutation_only(self) -> bool:
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ExtendAction(SequenceDeltasAction[_S_co], SequenceAction[_S_co], Generic[_S_co]):
    def __init__(self, old_sequence_length: int, extend_by: tuple[_S_co, ...]):
        self.old_sequence_length = old_sequence_length
        self._items = extend_by

    @property
    def items(self) -> Iterable[_S_co]:
        return self._items

    @property
    def is_permutation_only(self) -> bool:
        return False

    @property
    def delta_actions(self) -> tuple[SequenceDeltaAction[_S_co], ...]:
        return tuple(SimpleInsertAction(i, item) for i, item in enumerate(self._items, start=self.old_sequence_length))

    def map(self, transformer: Callable[[_S_co], _T]) -> ExtendAction[_T]:
        return ExtendAction(self.old_sequence_length, tuple(transformer(item) for item in self._items))

    def __repr__(self):
        return f"{self.__class__.__name__}(old_sequence_length={self.old_sequence_length}, items={self._items})"


class ClearSequenceAction(SequenceAction[_S_co], ClearAction[_S_co], Generic[_S_co]):
    @property
    def is_permutation_only(self) -> bool:
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}()"


CLEAR_SEQUENCE_ACTION: ClearSequenceAction = ClearSequenceAction()
REVERSE_SEQUENCE_ACTION: ReverseAction = ReverseAction()


def clear_sequence_action() -> ClearSequenceAction[_S_co]:
    return CLEAR_SEQUENCE_ACTION  # type: ignore[return-value]


def reverse_sequence_action() -> ReverseAction[_S_co]:
    return REVERSE_SEQUENCE_ACTION  # type: ignore[return-value]
