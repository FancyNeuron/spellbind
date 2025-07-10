from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_clear_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.clear()
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.removed_observers.assert_called_once(((0, 1), (1, 2), (2, 3)))
    observers.added_observers.assert_not_called()


def test_clear_empty_does_not_notify():
    observable_list = ObservableList([])
    observers = OneParameterObserver(observable_list)
    observable_list.clear()
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_not_called()
