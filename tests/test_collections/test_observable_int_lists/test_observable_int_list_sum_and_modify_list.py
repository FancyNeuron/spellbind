import pytest

from conftest import OneParameterObserver
from spellbind.int_collections import ObservableIntList, IntValueList


@pytest.mark.parametrize("constructor", [ObservableIntList, IntValueList])
def test_sum_int_list_append_sequentially(constructor):
    int_list = constructor([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.append(4)
    assert summed.value == 10
    int_list.append(5)
    assert summed.value == 15
    int_list.append(6)
    assert summed.value == 21
    assert observer.calls == [10, 15, 21]


def test_sum_int_list_clear():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.clear()
    assert summed.value == 0
    observer.assert_called_once_with(0)


def test_sum_int_list_del_sequentially():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    del int_list[0]
    assert summed.value == 5
    del int_list[0]
    assert summed.value == 3
    del int_list[0]
    assert summed.value == 0
    assert observer.calls == [5, 3, 0]


def test_sum_int_list_del_slice():
    int_list = ObservableIntList([1, 2, 3, 4, 5])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 15
    del int_list[1:4]
    assert summed.value == 6
    assert observer.calls == [6]


def test_sum_int_list_extend():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.extend([4, 5])
    assert summed.value == 15
    int_list.extend([6])
    assert summed.value == 21
    assert observer.calls == [15, 21]


def test_sum_int_list_insert():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.insert(0, 4)
    assert summed.value == 10
    int_list.insert(2, 5)
    assert summed.value == 15
    int_list.insert(5, 6)
    assert summed.value == 21
    assert observer.calls == [10, 15, 21]


def test_sum_int_list_insert_all():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.insert_all(((1, 4), (2, 5), (3, 6)))
    assert summed.value == 21
    assert observer.calls == [21]


def test_sum_int_list_setitem():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list[0] = 4
    assert summed.value == 9
    int_list[1] = 5
    assert summed.value == 12
    int_list[2] = 6
    assert summed.value == 15
    assert observer.calls == [9, 12, 15]


def test_sum_int_list_set_slice():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list[0:3] = [4, 5, 6]
    assert summed.value == 15
    assert observer.calls == [15]


def test_sum_int_list_reverse():
    int_list = ObservableIntList([1, 2, 3])
    summed = int_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6
    int_list.reverse()
    assert summed.value == 6
    observer.assert_not_called()
