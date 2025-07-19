import pytest

from conftest import ValueSequenceObservers
from spellbind.actions import reverse_action
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.observable_sequences import ObservableList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_reverse_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list.reverse()
    assert observable_list == [3, 2, 1]
    assert observable_list.length_value.value == 3


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_reverse_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.reverse()
    assert observable_list == [3, 2, 1]
    assert observable_list.length_value.value == 3
    observers.assert_calls((0, 1, False), (0, 2, False), (0, 3, False), (0, 3, True), (1, 2, True), (2, 1, True))
    observers.assert_single_action(reverse_action())


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_reverse_empty_does_not_notify(constructor):
    observable_list = constructor([])
    observers = ValueSequenceObservers(observable_list)
    observable_list.reverse()
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_reverse_one_element_list_does_not_notify(constructor):
    observable_list = constructor([1])
    observers = ValueSequenceObservers(observable_list)
    observable_list.reverse()
    assert observable_list == [1]
    assert observable_list.length_value.value == 1
    observers.assert_not_called()
