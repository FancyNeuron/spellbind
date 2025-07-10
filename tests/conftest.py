from typing import Iterable, Any, overload, Collection
from unittest.mock import Mock

import pytest

from spellbind.collections import ObservableList, ObservableSequence


class Call:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.args == other.args and self.kwargs == other.kwargs
        elif isinstance(other, (int, float, str, bool)):
            if len(self.kwargs) > 0:
                return False
            if len(self.args) != 1:
                return False
            return self.args[0] == other
        elif isinstance(other, Collection):
            if len(self.kwargs) > 0:
                return False
            return self.args == other

        return False

    def __repr__(self):
        args_repr = ", ".join(repr(arg) for arg in self.args)
        kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
        return f"Call({args_repr}, {kwargs_repr})" if kwargs_repr else f"Call({args_repr})"


class Observer(Mock):
    calls: list[Call]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.calls.append(Call(*args, **kwargs))


class NoParametersObserver(Observer):
    def __call__(self):
        super().__call__()


class OneParameterObserver(Observer):
    def __call__(self, param0):
        super().__call__(param0)


class OneDefaultParameterObserver(Observer):
    def __call__(self, param0="default"):
        super().__call__(param0)


class TwoParametersObserver(Observer):
    def __call__(self, param0, param1):
        super().__call__(param0, param1)


class OneRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1="default"):
        super().__call__(param0, param1)


class TwoDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1"):
        super().__call__(param0, param1)


class ThreeParametersObserver(Observer):
    def __call__(self, param0, param1, param2):
        super().__call__(param0, param1, param2)


class ThreeDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1", param2="default2"):
        super().__call__(param0=param0, param1=param1, param2=param2)


class TwoRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1, param2="default2"):
        super().__call__(param0, param1, param2)


class Observers:
    def __init__(self, *observers: Observer):
        self._observers = tuple(observers)

    def __iter__(self):
        return iter(self._observers)

    def assert_not_called(self):
        for observer in self:
            observer.assert_not_called()


class SequencePairObservers(Observers):
    def __init__(self, observer: OneParameterObserver, index_observer: OneParameterObserver):
        self.observer = observer
        self.index_observer = index_observer
        super().__init__(self.observer, self.index_observer)

    @overload
    def assert_called_once(self, indices_with_values: Iterable[tuple[int, Any]]): ...

    @overload
    def assert_called_once(self, index: int, value: Any): ...

    def assert_called_once(self, index, value=None):
        if isinstance(index, int):
            self.observer.assert_called_once_with((value,))
            self.index_observer.assert_called_once_with(((index, value),))
        else:
            self.observer.assert_called_once_with(tuple(value for _, value in index))
            self.index_observer.assert_called_once_with(index)


class SequenceObservers(Observers):
    def __init__(self, observable_sequence: ObservableSequence):
        self.added_observer = OneParameterObserver()
        self.added_index_observer = OneParameterObserver()
        self.added_observers = SequencePairObservers(self.added_observer, self.added_index_observer)
        self.removed_observer = OneParameterObserver()
        self.removed_index_observer = OneParameterObserver()
        self.removed_observers = SequencePairObservers(self.removed_observer, self.removed_index_observer)
        observable_sequence.added_observable.observe(self.added_observer)
        observable_sequence.removed_observable.observe(self.removed_observer)
        observable_sequence.added_index_observable.observe(self.added_index_observer)
        observable_sequence.removed_index_observable.observe(self.removed_index_observer)
        super().__init__(*self.added_observers, *self.removed_observers)


@pytest.fixture
def fully_observed_list_123() -> tuple[tuple[tuple[OneParameterObserver, OneParameterObserver], tuple[OneParameterObserver, OneParameterObserver]], ObservableList]:
    added_observer = OneParameterObserver()
    removed_observer = OneParameterObserver()
    added_index_observer = OneParameterObserver()
    removed_index_observer = OneParameterObserver()
    observable_list = ObservableList([1, 2, 3])
    observable_list.added_observable.observe(added_observer)
    observable_list.removed_observable.observe(removed_observer)
    observable_list.added_index_observable.observe(added_index_observer)
    observable_list.removed_index_observable.observe(removed_index_observer)

    return ((added_observer, added_index_observer), (removed_observer, removed_index_observer)), observable_list
