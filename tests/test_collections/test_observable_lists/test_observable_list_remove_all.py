from typing import Iterable

import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_first_and_last_notifies_multiple_times(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.remove_all([1, 3])
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    observers.assert_removed_calls((0, 1), (1, 3))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_duplicate_element(constructor):
    observable_list = constructor([1, 2, 1, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.remove_all([1, 3, 1])
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    observers.assert_removed_calls((0, 1), (1, 1), (1, 3))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.remove_all((1, 3))
    assert observable_list == [2]
    assert observable_list.length_value.value == 1
    observers.assert_removed_calls((0, 1), (1, 3))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_empty_does_not_notify(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list.remove_all([])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_non_existing_raises(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list.remove_all([4])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("invalid_removes", [(1, 4), (4, 1), (4, 5), (1, 2, 4), (3, 2, 1, 4), (1, 1)])
@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_remove_all_partially_existing_raises_reverts_not_notifies(constructor, invalid_removes: Iterable[int]):
    observable_list = ObservableList([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list.remove_all(invalid_removes)
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_pop_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 1):
        observable_list.remove_all((1, 3))
