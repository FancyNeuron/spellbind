from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_observable_list_extend_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.extend((4, 5, 6))
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((3, 4), (4, 5), (5, 6))


def test_observable_list_extend_empty_does_not_notify():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.extend([])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()
