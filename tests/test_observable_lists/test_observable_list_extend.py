from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_observable_list_extend_notifies_multiple_times():
    observable_list = ObservableList([1, 2, 3])
    observer = OneParameterObserver()
    observable_list.added_observable.observe_single(observer)
    observable_list.extend([4, 5, 6])
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6
    assert observer.calls == [4, 5, 6]


def test_observable_list_extend_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.extend((4, 5, 6))
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6
    observers.added_observers.assert_called_once(((3, 4), (4, 5), (5, 6)))
    observers.removed_observers.assert_not_called()


def test_observable_list_extend_empty_does_not_notify():
    observable_list = ObservableList([1, 2, 3])
    observer = OneParameterObserver()
    observable_list.added_observable.observe_single(observer)
    observable_list.extend([])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    assert observer.calls == []
