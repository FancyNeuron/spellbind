import pytest

from conftest import ValueSequenceObservers
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.observable_sequences import ObservableList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_mul_zero_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    multiplied = observable_list * 0
    assert multiplied == []
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
def test_mul_one_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    multiplied = observable_list * 1
    assert multiplied == [1, 2, 3]
    assert multiplied is not observable_list
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList])
def test_mul_two_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    multiplied = observable_list * 2
    assert multiplied == [1, 2, 3, 1, 2, 3]
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()
