import pytest

from conftest import OneParameterObserver, ValueSequenceObservers
from spellbind.actions import SimpleChangedAction
from spellbind.int_values import IntVariable
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_initialize_observable_list(constructor):
    observable_list = constructor([1, 2, 3])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3


def test_value_list_mixed_init_change_variable():
    variable = IntVariable(4)
    value_list = ValueList([1, 2, 3, variable])
    observers = ValueSequenceObservers(value_list)
    variable.value = 5
    assert value_list == [1, 2, 3, 5]
    assert value_list.length_value.value == 4
    observers.assert_calls((4, False), (5, True))
    observers.assert_actions(SimpleChangedAction(new_item=5, old_item=4))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def empty_list_is_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    assert not observable_list.on_change.is_observed()
    assert not observable_list.delta_observable.is_observed()
    assert not observable_list.length_value.is_observed()


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_changing_length_value_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    length_observer = OneParameterObserver()
    length_value = observable_list.length_value
    length_value.observe(length_observer)
    assert length_value.value == 3
    observable_list.append(4)
    assert length_value.value == 4
    observable_list.remove(2)
    assert length_value.value == 3
    assert length_observer.calls == [4, 3]


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_to_str(constructor):
    observable_list = constructor([1, 2, 3])
    assert str(observable_list) == "[1, 2, 3]"
