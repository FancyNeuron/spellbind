import pytest

from conftest import OneParameterObserver, ValueSequenceObservers, \
    assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import clear_action
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList
from spellbind.int_collections import ObservableIntList, IntValueList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_clear_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list.clear()
    assert observable_list == []
    assert observable_list.length_value.value == 0


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_clear_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.clear()
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))
    observers.assert_single_action(clear_action())


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_clear_empty_does_not_notify(constructor):
    observable_list = constructor([])
    observers = OneParameterObserver(observable_list)
    observable_list.clear()
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_clear_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 0):
        observable_list.clear()


def test_clear_value_list_changing_value_does_not_notify():
    variable = IntVariable(3)
    value_list = IntValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    value_list.clear()
    variable.value = 4
    assert value_list == []
    assert value_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))
    observers.assert_single_action(clear_action())
