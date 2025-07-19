from spellbind.int_collections import ObservableIntList


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
