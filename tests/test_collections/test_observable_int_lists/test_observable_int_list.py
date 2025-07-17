from spellbind.int_collections import ObservableIntList


def test_derive_commutative_reverse_not_called():
    int_list = ObservableIntList([1, 2, 3])
    calls = []

    def add_reducer(x, y):
        calls.append("added")
        return 0

    def remove_reducer(x, y):
        calls.append("removed")
        return 0
    summed = int_list.reduce(add_reducer=add_reducer, remove_reducer=remove_reducer, empty_value=1)
    calls.clear()
    int_list.reverse()
    assert calls == []
