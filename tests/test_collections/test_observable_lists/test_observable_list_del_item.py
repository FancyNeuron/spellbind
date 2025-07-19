import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import SimpleRemoveAtIndexAction, SimpleRemoveAtIndicesAction
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList
from spellbind.int_collections import ObservableIntList, IntValueList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    del observable_list[1]
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_slice_unobserved(constructor):
    observable_list = constructor([1, 2, 3, 4, 5])
    del observable_list[1:3]
    assert observable_list == [1, 4, 5]
    assert observable_list.length_value.value == 3


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    del observable_list[1]
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((1, 2))
    observers.assert_single_action(SimpleRemoveAtIndexAction(1, 2))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_invalid_index_raises(constructor):
    observable_list = constructor([1, 2, 3])
    with pytest.raises(IndexError):
        del observable_list[3]
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_slice(constructor):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    del observable_list[1:3]
    assert observable_list == [1, 4, 5]
    assert observable_list.length_value.value == 3
    observers.assert_removed_calls((1, 2), (1, 3))
    observers.assert_single_action(SimpleRemoveAtIndicesAction(((1, 2), (2, 3))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_stepped_slice(constructor):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    del observable_list[::2]
    assert observable_list == [2, 4]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((0, 1), (1, 3), (2, 5))
    observers.assert_single_action(SimpleRemoveAtIndicesAction(((0, 1), (2, 3), (4, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_empty_list(constructor):
    observable_list = constructor([])
    observers = ValueSequenceObservers(observable_list)
    del observable_list[0:0]
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_item_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 2):
        del observable_list[1]


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_del_slice_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3, 4, 5])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 2):
        del observable_list[1:4]


def test_del_item_value_list_changing_value_does_not_notify():
    variable = IntVariable(3)
    value_list = IntValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    del value_list[2]
    variable.value = 4
    assert value_list == [1, 2]
    assert value_list.length_value.value == 2
    observers.assert_removed_calls((2, 3))
    observers.assert_single_action(SimpleRemoveAtIndexAction(2, 3))
