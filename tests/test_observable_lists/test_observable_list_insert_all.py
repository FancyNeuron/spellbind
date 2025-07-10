from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_insert_all_in_order_notifies():
    observable_list = ObservableList([1, 2, 3, 4])
    observers = SequenceObservers(observable_list)
    observable_list.insert_all(((1, 4), (3, 5)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.added_observers.assert_called_once(((1, 4), (3, 5)))
    observers.removed_observers.assert_not_called()


def test_insert_all_out_of_order_notifies():
    observable_list = ObservableList([1, 2, 3, 4])
    observers = SequenceObservers(observable_list)
    observable_list.insert_all(((3, 5), (1, 4)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.added_observers.assert_called_once(((1, 4), (3, 5)))
    observers.removed_observers.assert_not_called()


def test_insert_nothing():
    observable_list = ObservableList([1, 2, 3, 4])
    observers = SequenceObservers(observable_list)
    observable_list.insert_all(())
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4
    observers.assert_not_called()
