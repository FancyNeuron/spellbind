from typing import Iterable

import pytest

from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_remove_all_first_and_last_notifies_multiple_times():
    observable_list = ObservableList([1, 2, 3])
    observer = OneParameterObserver()
    observable_list.removed_observable.observe_single(observer)
    observable_list.remove_all([1, 3])
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    assert observer.calls == [1, 3]


def test_remove_all_twice_notifies_multiple_times():
    observable_list = ObservableList([1, 2, 1, 3])
    observer = OneParameterObserver()
    observable_list.removed_observable.observe_single(observer)
    observable_list.remove_all([1, 3, 1])
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    assert observer.calls == [1, 1, 3]


def test_remove_all_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.remove_all((1, 3))
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    observers.removed_observers.assert_called_once(((0, 1), (2, 3)))


def test_remove_all_empty_does_not_notify():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.remove_all([])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


def test_remove_all_non_existing_raises():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list.remove_all([4])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("invalid_removes", [(1, 4), (4, 1), (4, 5), (1, 2, 4), (3, 2, 1, 4), (1, 1)])
def test_remove_all_partially_existing_raises_reverts_not_notifies(invalid_removes: Iterable[int]):
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list.remove_all(invalid_removes)
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()
