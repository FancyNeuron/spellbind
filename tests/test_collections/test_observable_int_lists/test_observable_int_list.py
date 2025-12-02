from conftest import OneParameterObserver
from spellbind.int_collections import ObservableIntList
from spellbind.observable_sequences import ObservableList


def test_combine_ints():
    int_list = ObservableIntList([1, 2, 3])
    combined = int_list.combine_to_int(combiner=sum)
    assert combined.value == 6


def test_derive_commutative_reverse_not_called():
    int_list = ObservableIntList([1, 2, 3])
    calls = []

    def reducer(x, y):
        calls.append("added")
        return 0

    summed = int_list.reduce(add_reducer=reducer, remove_reducer=reducer, initial=1)
    calls.clear()
    int_list.reverse()
    assert calls == []


def test_derive_commutative_reduce_order_not_called():
    int_list = ObservableIntList([1, 2, 3])
    calls = []

    def add_reducer(x, y):
        calls.append(f"added {y}")
        return 0

    def remove_reducer(x, y):
        calls.append(f"removed {y}")
        return 0
    summed = int_list.reduce(add_reducer=add_reducer, remove_reducer=remove_reducer, initial=1)
    calls.clear()
    int_list.append(1)
    int_list.append(2)
    int_list.append(3)
    int_list.pop(1)
    assert calls == ["added 1", "added 2", "added 3", "removed 2"]


def test_reduce_to_int_string_lengths():
    string_list = ObservableList(["a", "bb", "ccc"])
    total_length = string_list.reduce_to_int(
        add_reducer=lambda acc, s: acc + len(s),
        remove_reducer=lambda acc, s: acc - len(s),
        initial=0
    )
    assert total_length.value == 6


def test_reduce_to_int_string_lengths_append():
    string_list = ObservableList(["a", "bb", "ccc"])
    total_length = string_list.reduce_to_int(
        add_reducer=lambda acc, s: acc + len(s),
        remove_reducer=lambda acc, s: acc - len(s),
        initial=0
    )
    observer = OneParameterObserver()
    total_length.observe(observer)

    assert total_length.value == 6

    string_list.append("dddd")
    assert total_length.value == 10
    observer.assert_called_once_with(10)


def test_reduce_to_int_string_lengths_remove():
    string_list = ObservableList(["a", "bb", "ccc"])
    total_length = string_list.reduce_to_int(
        add_reducer=lambda acc, s: acc + len(s),
        remove_reducer=lambda acc, s: acc - len(s),
        initial=0
    )
    observer = OneParameterObserver()
    total_length.observe(observer)

    assert total_length.value == 6

    string_list.remove("bb")
    assert total_length.value == 4
    observer.assert_called_once_with(4)


def test_reduce_to_int_string_lengths_setitem():
    string_list = ObservableList(["a", "bb", "ccc"])
    total_length = string_list.reduce_to_int(
        add_reducer=lambda acc, s: acc + len(s),
        remove_reducer=lambda acc, s: acc - len(s),
        initial=0
    )
    observer = OneParameterObserver()
    total_length.observe(observer)

    assert total_length.value == 6

    string_list[1] = "dddd"
    assert total_length.value == 8
    observer.assert_called_once_with(8)


def test_reduce_to_int_string_lengths_reverse():
    string_list = ObservableList(["a", "bb", "ccc"])
    total_length = string_list.reduce_to_int(
        add_reducer=lambda acc, s: acc + len(s),
        remove_reducer=lambda acc, s: acc - len(s),
        initial=0
    )
    observer = OneParameterObserver()
    total_length.observe(observer)

    assert total_length.value == 6

    string_list.reverse()
    assert total_length.value == 6
    observer.assert_not_called()
