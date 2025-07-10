import pytest

from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_del_item_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    del observable_list[1]
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((1, 2))


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
    observers.assert_removed_calls((1, 2), (1, 3))


def test_del_item_stepped_slice():
    observable_list = ObservableList([1, 2, 3, 4, 5])
    observers = SequenceObservers(observable_list)
    del observable_list[::2]
    assert observable_list == [2, 4]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((0, 1), (1, 3), (2, 5))
