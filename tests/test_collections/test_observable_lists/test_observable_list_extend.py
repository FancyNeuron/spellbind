import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleExtendAction
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_observable_list_extend_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list.extend((4, 5, 6))
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_observable_list_extend_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.extend((4, 5, 6))
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6
    observers.assert_added_calls((3, 4), (4, 5), (5, 6))
    observers.assert_single_action(SimpleExtendAction(old_sequence_length=3, extend_by=(4, 5, 6)))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_observable_list_extend_empty_does_not_notify(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.extend([])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_extend_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 5):
        observable_list.extend((4, 5))
