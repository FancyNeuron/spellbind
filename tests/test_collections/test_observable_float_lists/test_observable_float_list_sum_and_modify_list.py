import pytest

from conftest import OneParameterObserver
from spellbind.float_collections import ObservableFloatList, FloatValueList


@pytest.mark.parametrize("constructor", [ObservableFloatList, FloatValueList])
def test_sum_float_list_append_sequentially(constructor):
    float_list = constructor([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.append(4.0)
    assert summed.value == 10.0
    float_list.append(5.0)
    assert summed.value == 15.0
    float_list.append(6.0)
    assert summed.value == 21.0
    assert observer.calls == [10.0, 15.0, 21.0]


def test_sum_float_list_clear():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.clear()
    assert summed.value == 0.0
    observer.assert_called_once_with(0.0)


def test_sum_float_list_del_sequentially():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    del float_list[0]
    assert summed.value == 5.0
    del float_list[0]
    assert summed.value == 3.0
    del float_list[0]
    assert summed.value == 0.0
    assert observer.calls == [5.0, 3.0, 0.0]


def test_sum_float_list_del_slice():
    float_list = ObservableFloatList([1.0, 2.0, 3.0, 4.0, 5.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 15.0
    del float_list[1:4]
    assert summed.value == 6.0
    assert observer.calls == [6.0]


def test_sum_float_list_extend():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.extend([4.0, 5.0])
    assert summed.value == 15.0
    float_list.extend([6.0])
    assert summed.value == 21.0
    assert observer.calls == [15.0, 21.0]


def test_sum_float_list_insert():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.insert(0, 4.0)
    assert summed.value == 10.0
    float_list.insert(2, 5.0)
    assert summed.value == 15.0
    float_list.insert(5, 6.0)
    assert summed.value == 21.0
    assert observer.calls == [10.0, 15.0, 21.0]


def test_sum_float_list_insert_all():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.insert_all(((1, 4.0), (2, 5.0), (3, 6.0)))
    assert summed.value == 21.0
    assert observer.calls == [21.0]


def test_sum_float_list_setitem():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list[0] = 4.0
    assert summed.value == 9.0
    float_list[1] = 5.0
    assert summed.value == 12.0
    float_list[2] = 6.0
    assert summed.value == 15.0
    assert observer.calls == [9.0, 12.0, 15.0]


def test_sum_float_list_set_slice():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list[0:3] = [4.0, 5.0, 6.0]
    assert summed.value == 15.0
    assert observer.calls == [15.0]


def test_sum_float_list_reverse():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    summed = float_list.summed
    observer = OneParameterObserver()
    summed.observe(observer)
    assert summed.value == 6.0
    float_list.reverse()
    assert summed.value == 6.0
    observer.assert_not_called()
