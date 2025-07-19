import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleRemoveAtIndexAction
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList
from spellbind.int_collections import ObservableIntList, IntValueList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_remove_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.remove(2)
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((1, 2))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_remove_non_existing_raises(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list.remove(4)
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_pop_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 2):
        observable_list.remove(2)


def test_remove_item_list_changing_value_does_not_notify():
    variable = IntVariable(3)
    value_list = IntValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    value_list.remove(variable)
    variable.value = 4
    assert value_list == [1, 2]
    assert value_list.length_value.value == 2
    observers.assert_removed_calls((2, 3))
    observers.assert_actions(SimpleRemoveAtIndexAction(2, 3))


def test_remove_literal_which_is_same_as_variable_raises():
    variable = IntVariable(3)
    value_list = IntValueList([1, 2, variable])
    with pytest.raises(ValueError):
        value_list.remove(3)
    assert value_list == [1, 2, variable]
    assert value_list.length_value.value == 3
