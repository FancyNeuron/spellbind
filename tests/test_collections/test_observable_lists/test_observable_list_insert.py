import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleInsertAction, SimpleChangedAction
from spellbind.int_values import IntVariable
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list.insert(1, 4)
    assert observable_list == [1, 4, 2, 3]
    assert observable_list.length_value.value == 4


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.insert(1, 4)
    assert observable_list == [1, 4, 2, 3]
    assert observable_list.length_value.value == 4
    observers.assert_added_calls((1, 4))
    observers.assert_single_action(SimpleInsertAction(1, 4))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_insert_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 4):
        observable_list.insert(1, 4)


def test_insert_item_list_changing_value_notifies():
    value_list = ValueList([1, 2, 3])
    observers = ValueSequenceObservers(value_list)
    variable = IntVariable(4)
    value_list.insert(2, variable)
    variable.value = 5
    assert value_list == [1, 2, 5, 3]
    assert value_list.length_value.value == 4
    observers.assert_calls((2, 4, True), (4, False), (5, True))
    observers.assert_actions(SimpleInsertAction(2, 4),
                             SimpleChangedAction(new_item=5, old_item=4))
