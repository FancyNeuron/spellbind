import pytest

from conftest import OneParameterObserver, ValueSequenceObservers, values_factories
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.int_values import IntVariable, IntConstant
from spellbind.observable_sequences import ObservableList, SimpleValueChangedMultipleTimesAction
from spellbind.str_collections import StrValueList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList, StrValueList])
def test_initialize_empty(constructor):
    int_list = constructor()
    assert len(int_list) == 0
    assert list(int_list) == []


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_initialize_observable_list(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3


def test_value_list_mixed_init_change_variable_contained_once():
    variable = IntVariable(4)
    value_list = IntValueList([1, 2, 3, variable])
    observers = ValueSequenceObservers(value_list)
    variable.value = 5
    assert value_list.as_raw_list() == [1, 2, 3, 5]
    assert value_list.length_value.value == 4
    observers.assert_calls((4, False), (5, True))
    observers.assert_actions(SimpleValueChangedMultipleTimesAction(new_item=5, old_item=4, count=1))


def test_value_list_mixed_init_change_variable_contained_twice():
    variable = IntVariable(4)
    value_list = IntValueList([1, 2, 3, variable, variable])
    observers = ValueSequenceObservers(value_list)
    variable.value = 5
    assert value_list.as_raw_list() == [1, 2, 3, 5, 5]
    assert value_list.length_value.value == 5
    observers.assert_calls((4, False), (5, True), (4, False), (5, True))
    observers.assert_actions(SimpleValueChangedMultipleTimesAction(new_item=5, old_item=4, count=2))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
def empty_list_is_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    assert not observable_list.on_change.is_observed()
    assert not observable_list.delta_observable.is_observed()
    assert not observable_list.length_value.is_observed()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
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


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
def test_to_str(constructor):
    observable_list = constructor([1, 2, 3])
    assert str(observable_list) == "[1, 2, 3]"


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
def test_list_of_observable_list(constructor):
    observable_list = constructor([1, 2, 3])
    flat_list = list(observable_list)
    assert flat_list == [1, 2, 3]


def test_list_of_int_value_list():
    observable_list = IntValueList([1, 2, 3])
    flat_list = list(observable_list)
    assert flat_list == [IntConstant.of(1), IntConstant.of(2), IntConstant.of(3)]
