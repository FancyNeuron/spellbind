import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after, \
    values_factories
from spellbind.actions import SimpleInsertAllAction
from spellbind.observable_sequences import ObservableList
from spellbind.int_collections import ObservableIntList, IntValueList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_insert_all_unobserved(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4])
    observable_list.insert_all(values_factory((1, 4), (3, 5)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_insert_all_in_order_notifies(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(values_factory((1, 4), (3, 5)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((1, 4), (4, 5))
    observers.assert_single_action(SimpleInsertAllAction(sorted_index_with_items=((1, 4), (3, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_insert_all_out_of_order_notifies(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(values_factory((3, 5), (1, 4)))
    assert observable_list == [1, 4, 2, 3, 5, 4]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((1, 4), (4, 5))
    observers.assert_single_action(SimpleInsertAllAction(sorted_index_with_items=((1, 4), (3, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_insert_nothing(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert_all(values_factory())
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_insert_all_length_already_set_but_notifies_after(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 5):
        observable_list.insert_all(values_factory((1, 4), (2, 5)))
