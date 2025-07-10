import pytest

from conftest import OneParameterObserver, SequenceObservers
from spellbind.collections import ObservableList


def test_initialize_observable_list():
    observable_list = ObservableList([1, 2, 3])
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3


def test_remove_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.remove(2)
    assert observable_list == [1, 3]
    assert observable_list.length_value.value == 2
    observers.assert_removed_calls((1, 2))


def test_changing_length_value_notifies():
    observable_list = ObservableList([1, 2, 3])
    length_observer = OneParameterObserver()
    length_value = observable_list.length_value
    length_value.observe(length_observer)
    assert length_value.value == 3
    observable_list.append(4)
    assert length_value.value == 4
    observable_list.remove(2)
    assert length_value.value == 3
    assert length_observer.calls == [4, 3]


def test_reverse_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list.reverse()
    assert observable_list == [3, 2, 1]
    assert observable_list.length_value.value == 3
    observers.assert_calls((0, 1, False), (0, 2, False), (0, 3, False), (0, 3, True), (1, 2, True), (2, 1, True))


def test_iadd_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list += (4, 5)
    assert observable_list == [1, 2, 3, 4, 5]
    assert observable_list.length_value.value == 5
    observers.assert_added_calls((3, 4), (4, 5))


def test_iadd_nothing_does_not_notify():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list += []
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


def test_imul_zero_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list *= 0
    assert observable_list == []
    assert observable_list.length_value.value == 0
    observers.assert_removed_calls((0, 1), (0, 2), (0, 3))


def test_imul_one_does_not_notify():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list *= 1
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()


@pytest.mark.parametrize("mul", [2, 3, 4])
def test_imul_notifies(mul: int):
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list *= mul
    assert observable_list == [1, 2, 3] * mul
    assert observable_list.length_value.value == 3 * mul
    added_indices = tuple((i + 3, (i % 3) + 1) for i in range(3 * (mul-1)))
    observers.assert_added_calls(*added_indices)
