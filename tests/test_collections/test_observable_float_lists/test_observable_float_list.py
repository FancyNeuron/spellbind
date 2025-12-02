from conftest import OneParameterObserver
from spellbind.float_collections import ObservableFloatList
from spellbind.observable_sequences import ObservableList


def test_combine_floats():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    combined = float_list.combine_to_float(combiner=sum)
    assert combined.value == 6.0


def test_derive_commutative_reverse_not_called():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    calls = []

    def reducer(x, y):
        calls.append("added")
        return 0.0

    summed = float_list.reduce(add_reducer=reducer, remove_reducer=reducer, initial=1.0)
    calls.clear()
    float_list.reverse()
    assert calls == []


def test_derive_commutative_reduce_order_not_called():
    float_list = ObservableFloatList([1.0, 2.0, 3.0])
    calls = []

    def add_reducer(x, y):
        calls.append(f"added {y}")
        return 0.0

    def remove_reducer(x, y):
        calls.append(f"removed {y}")
        return 0.0
    summed = float_list.reduce(add_reducer=add_reducer, remove_reducer=remove_reducer, initial=1.0)
    calls.clear()
    float_list.append(1.0)
    float_list.append(2.0)
    float_list.append(3.0)
    float_list.pop(1)
    assert calls == ["added 1.0", "added 2.0", "added 3.0", "removed 2.0"]


def test_reduce_to_float_half_string_lengths():
    string_list = ObservableList(["a", "bb", "ccc"])
    half_length = string_list.reduce_to_float(
        add_reducer=lambda acc, s: acc + len(s) / 2.0,
        remove_reducer=lambda acc, s: acc - len(s) / 2.0,
        initial=0.0
    )
    assert half_length.value == 3.0


def test_reduce_to_float_half_string_lengths_append():
    string_list = ObservableList(["a", "bb", "ccc"])
    half_length = string_list.reduce_to_float(
        add_reducer=lambda acc, s: acc + len(s) / 2.0,
        remove_reducer=lambda acc, s: acc - len(s) / 2.0,
        initial=0.0
    )
    observer = OneParameterObserver()
    half_length.observe(observer)

    assert half_length.value == 3.0

    string_list.append("dddd")
    assert half_length.value == 5.0
    observer.assert_called_once_with(5.0)


def test_reduce_to_float_half_string_lengths_remove():
    string_list = ObservableList(["a", "bb", "ccc"])
    half_length = string_list.reduce_to_float(
        add_reducer=lambda acc, s: acc + len(s) / 2.0,
        remove_reducer=lambda acc, s: acc - len(s) / 2.0,
        initial=0.0
    )
    observer = OneParameterObserver()
    half_length.observe(observer)

    assert half_length.value == 3.0

    string_list.remove("bb")
    assert half_length.value == 2.0
    observer.assert_called_once_with(2.0)


def test_reduce_to_float_half_string_lengths_setitem():
    string_list = ObservableList(["a", "bb", "ccc"])
    half_length = string_list.reduce_to_float(
        add_reducer=lambda acc, s: acc + len(s) / 2.0,
        remove_reducer=lambda acc, s: acc - len(s) / 2.0,
        initial=0.0
    )
    observer = OneParameterObserver()
    half_length.observe(observer)

    assert half_length.value == 3.0

    string_list[1] = "dddd"
    assert half_length.value == 4.0
    observer.assert_called_once_with(4.0)


def test_reduce_to_float_half_string_lengths_reverse():
    string_list = ObservableList(["a", "bb", "ccc"])
    half_length = string_list.reduce_to_float(
        add_reducer=lambda acc, s: acc + len(s) / 2.0,
        remove_reducer=lambda acc, s: acc - len(s) / 2.0,
        initial=0.0
    )
    observer = OneParameterObserver()
    half_length.observe(observer)

    assert half_length.value == 3.0

    string_list.reverse()
    assert half_length.value == 3.0
    observer.assert_not_called()
