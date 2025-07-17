import pytest

from conftest import OneParameterObserver, ValueSequenceObservers, \
    assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleRemoveAtIndexAction
from spellbind.int_values import IntVariable
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_pop_last_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    popped_item = observable_list.pop()
    assert popped_item == 3
    assert observable_list == [1, 2]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((2, 3))
    observers.assert_actions(SimpleRemoveAtIndexAction(2, 3))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_pop_first_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    popped_item = observable_list.pop(0)
    assert popped_item == 1
    assert observable_list == [2, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((0, 1))
    observers.assert_actions(SimpleRemoveAtIndexAction(0, 1))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_pop_invalid_index(constructor):
    observable_list = constructor([1, 2, 3])
    observers = OneParameterObserver(observable_list)
    with pytest.raises(IndexError):
        observable_list.pop(5)
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_pop_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 2):
        observable_list.pop(1)


def test_pop_item_list_changing_value_does_not_notify():
    variable = IntVariable(3)
    value_list = ValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    popped_item = value_list.pop(2)
    variable.value = 4
    assert popped_item == 3
    assert value_list == [1, 2]
    assert value_list.length_value.value == 2
    observers.assert_removed_calls((2, 3))
    observers.assert_actions(SimpleRemoveAtIndexAction(2, 3))
