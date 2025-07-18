import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after, \
    values_factories
from spellbind.actions import SimpleExtendAction
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList, SimpleValueChangedMultipleTimesAction


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_iadd_notifies(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list += values_factory(4, 5)
    assert observable_list == [1, 2, 3, 4, 5]
    assert observable_list.length_value.value == 5
    observers.assert_added_calls((3, 4), (4, 5))
    observers.assert_single_action(SimpleExtendAction(3, (4, 5)))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_iadd_nothing_does_not_notify(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list += []
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_iadd_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 5):
        observable_list += (4, 5)


def test_iadd_item_list_changing_value_notifies():
    value_list = IntValueList([1, 2, 3])
    observers = ValueSequenceObservers(value_list)
    variable = IntVariable(4)
    value_list += [variable, 5, 6]
    variable.value = 7
    assert value_list.as_raw_list() == [1, 2, 3, 7, 5, 6]
    assert value_list.length_value.value == 6
    observers.assert_calls((3, 4, True), (4, 5, True), (5, 6, True), (4, False), (7, True))
    observers.assert_actions(SimpleExtendAction(3, (4, 5, 6)),
                             SimpleValueChangedMultipleTimesAction(new_item=7, old_item=4))
