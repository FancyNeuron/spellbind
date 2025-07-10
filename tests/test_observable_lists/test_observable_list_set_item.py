import pytest

from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_observable_list_set_item_notifies():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    observable_list[1] = 4
    assert observable_list == [1, 4, 3]
    assert observable_list.length_value.value == 3
    observers.assert_calls((1, 2, False), (1, 4, True))


def test_observable_list_set_item_out_of_range():
    observable_list = ObservableList([1, 2, 3])
    observers = SequenceObservers(observable_list)
    with pytest.raises(IndexError):
        observable_list[3] = 4
    observers.assert_not_called()
