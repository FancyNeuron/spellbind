import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import clear_action, SimpleExtendAction, SimpleChangedAction
from spellbind.int_values import IntVariable
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_zero_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list *= 0
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))
    observers.assert_single_action(clear_action())


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_negative_one_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list *= -1
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))
    observers.assert_single_action(clear_action())


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_one_does_not_notify(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list *= 1
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("mul", [2, 3, 4])
@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_notifies(constructor, mul: int):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list *= mul
    assert observable_list == [1, 2, 3] * mul
    assert observable_list.length_value.value == 3 * mul
    added_indices = tuple((i + 3, (i % 3) + 1) for i in range(3 * (mul-1)))
    observers.assert_added_calls(*added_indices)
    observers.assert_single_action(SimpleExtendAction(3, (1, 2, 3) * (mul - 1)))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_zero_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 0):
        observable_list *= 0


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_imul_two_length_already_set_but_notifies_after(constructor):
    observable_list = constructor([1, 2, 3])
    with assert_length_changed_during_action_events_but_notifies_after(observable_list, 6):
        observable_list *= 2


def test_imul_zero_item_value_list_changing_value_does_not_notify():
    variable = IntVariable(3)
    value_list = ValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    value_list *= 0
    variable.value = 4
    assert value_list == []
    assert value_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))
    observers.assert_single_action(clear_action())


def test_imul_one_item_list_changing_value_does_not_notify():
    value_list = ValueList([1, 2, IntVariable(3)])
    observers = ValueSequenceObservers(value_list)
    value_list *= 1
    assert value_list == [1, 2, 3]
    assert value_list.length_value.value == 3
    observers.assert_not_called()


def test_imul_two_item_list_changing_value_changes_two_values():
    variable = IntVariable(3)
    value_list = ValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    value_list *= 2
    variable.value = 4
    assert value_list == [1, 2, 4, 1, 2, 4]
    assert value_list.length_value.value == 6
    observers.assert_calls((3, 1, True), (4, 2, True), (5, 3, True), (3, False), (4, True), (3, False), (4, True))
    observers.assert_actions(SimpleExtendAction(3, (1, 2, 3)),
                             SimpleChangedAction(new_item=4, old_item=3),
                             SimpleChangedAction(new_item=4, old_item=3))


def test_imul_three_item_list_changing_value_changes_three_values():
    variable = IntVariable(3)
    value_list = ValueList([1, 2, variable])
    observers = ValueSequenceObservers(value_list)
    value_list *= 3
    variable.value = 4
    assert value_list == [1, 2, 4, 1, 2, 4, 1, 2, 4]
    assert value_list.length_value.value == 9
    observers.assert_calls((3, 1, True), (4, 2, True), (5, 3, True),
                           (6, 1, True), (7, 2, True), (8, 3, True),
                           (3, False), (4, True),
                           (3, False), (4, True),
                           (3, False), (4, True))
    observers.assert_actions(SimpleExtendAction(3, (1, 2, 3, 1, 2, 3)),
                             SimpleChangedAction(new_item=4, old_item=3),
                             SimpleChangedAction(new_item=4, old_item=3),
                             SimpleChangedAction(new_item=4, old_item=3))
