import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleInsertAction
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList, SimpleValueChangedMultipleTimesAction


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_append_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list.append(4)
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_append_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.append(4)
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4
    observers.assert_added_calls((3, 4))
    observers.assert_single_action(SimpleInsertAction(3, 4))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_append_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 4):
        observable_list.append(4)


def test_change_appended_and_change_value_notifies():
    value_list = IntValueList([1, 2, 3])
    observers = ValueSequenceObservers(value_list)
    variable = IntVariable(4)
    value_list.append(variable)
    variable.value = 5
    assert value_list.as_raw_list() == [1, 2, 3, 5]
    assert value_list.length_value.value == 4
    observers.assert_calls((3, 4, True), (4, False), (5, True))
    observers.assert_actions(SimpleInsertAction(3, 4), SimpleValueChangedMultipleTimesAction(new_item=5, old_item=4))
