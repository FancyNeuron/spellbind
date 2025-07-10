from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_map_str_list_to_lengths_set_item():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 3]
    observable_list[1] = "blueberry"
    assert list(mapped) == [5, 9, 3]


def test_map_str_list_to_lengths_append():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 3]
    observable_list.append("blueberry")
    assert list(mapped) == [5, 6, 3, 9]


def test_map_str_list_to_lengths_insert():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 3]
    observable_list.insert(1, "blueberry")
    assert list(mapped) == [5, 9, 6, 3]


def test_map_str_list_to_lengths_remove():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.remove("banana")
    assert list(mapped) == [5, 3]
    mapped_observers.assert_removed_calls((1, 6))


def test_map_str_list_to_lengths_insert_all():
    observable_list = ObservableList(["apple", "banana", "fig", "plum"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3, 4]
    observable_list.insert_all([(1, "blueberry"), (3, "apricot")])
    assert list(mapped) == [5, 9, 6, 3, 7, 4]
    mapped_observers.assert_added_calls((1, 9), (4, 7))


def test_map_str_list_to_lengths_insert_all_out_of_order():
    observable_list = ObservableList(["apple", "banana", "fig", "plum"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3, 4]
    observable_list.insert_all([(3, "apricot"), (1, "blueberry")])
    assert list(mapped) == [5, 9, 6, 3, 7, 4]
    mapped_observers.assert_added_calls((1, 9), (4, 7))


def test_map_str_list_to_lengths_clear():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.clear()
    assert list(mapped) == []
    mapped_observers.assert_removed_calls((0, 5), (0, 6), (0, 3))


def test_map_str_list_to_lengths_reverse():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.reverse()
    assert list(mapped) == [3, 6, 5]
    mapped_observers.assert_calls((0, 5, False), (0, 6, False), (0, 3, False), (0, 3, True), (1, 6, True), (2, 5, True))


def test_map_str_list_to_lengths_get_item():
    observable_list = ObservableList(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert mapped[0] == 5
    assert mapped[1] == 6
    assert mapped[2] == 3
