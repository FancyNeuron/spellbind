import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleInsertAllAction
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_all_unobserved(constructor):
    observable_list = constructor([1, 2, 3, 4])
    observable_list.insert_all(((1, 4), (3, 5)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_all_in_order_notifies(constructor):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(((1, 4), (3, 5)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((1, 4), (4, 5))
    observers.assert_single_action(SimpleInsertAllAction(sorted_index_with_items=((1, 4), (3, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_all_out_of_order_notifies(constructor):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(((3, 5), (1, 4)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((1, 4), (4, 5))
    observers.assert_single_action(SimpleInsertAllAction(sorted_index_with_items=((1, 4), (3, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_nothing(constructor):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(())
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_all_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 5):
        observable_list.insert_all(((1, 4), (2, 5)))
