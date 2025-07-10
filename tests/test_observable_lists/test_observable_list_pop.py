import pytest

from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_pop_last_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    popped_item = observable_list.pop()
    assert popped_item == 3
    assert observable_list == [1, 2]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((2, 3))


def test_pop_first_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    popped_item = observable_list.pop(0)
    assert popped_item == 1
    assert observable_list == [2, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((0, 1))


def test_pop_invalid_index():
    observable_list = ObservableList([1, 2, 3])
    observers = OneParameterObserver(observable_list)
    with pytest.raises(IndexError):
        observable_list.pop(5)
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()
