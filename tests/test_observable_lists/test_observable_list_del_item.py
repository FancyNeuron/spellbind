import pytest

from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_del_item_notifies():
    observable_list = ObservableList([1, 2, 3])
    removed_observer = OneParameterObserver()
    observable_list.removed_observable.observe_single(removed_observer)
    del observable_list[1]
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2
    removed_observer.assert_called_once_with(2)


def test_del_item_invalid_index_raises():
    observable_list = ObservableList([1, 2, 3])
    with pytest.raises(IndexError):
        del observable_list[3]
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3


def test_del_item_slice():
    observable_list = ObservableList([1, 2, 3, 4, 5])
    observers = SequenceObservers(observable_list)
    del observable_list[1:3]
    assert observable_list == [1, 4, 5]
    assert observable_list.length_value.value == 3
    observers.removed_observers.assert_called_once(((1, 2), (2, 3)))


def test_del_item_stepped_slice():
    observable_list = ObservableList([1, 2, 3, 4, 5])
    observers = SequenceObservers(observable_list)
    del observable_list[::2]
    assert observable_list == [2, 4]
    assert observable_list.length_value.value == 2
    observers.removed_observers.assert_called_once(((0, 1), (2, 3), (4, 5)))
