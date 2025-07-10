from conftest import SequenceObservers
from spellbind.collections import ObservableList


def test_map_str_list_to_lengths_set_item():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 6]
    observable_list[1] = "blueberry"
    assert list(mapped) == [5, 9, 6]


def test_map_str_list_to_lengths_append():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 6]
    observable_list.append("blueberry")
    assert list(mapped) == [5, 6, 6, 9]


def test_map_str_list_to_lengths_insert():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 6]
    observable_list.insert(1, "blueberry")
    assert list(mapped) == [5, 9, 6, 6]


def test_map_str_list_to_lengths_remove():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 6]
    observable_list.remove("banana")
    assert list(mapped) == [5, 6]
    mapped_observers.removed_observers.assert_called_once(1, 6)


def test_map_str_list_to_lengths_insert_all():
    observable_list = ObservableList(["apple", "banana", "cherry", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 6, 3]
    observable_list.insert_all([(1, "blueberry"), (3, "date")])
    assert list(mapped) == [5, 9, 6, 6, 4, 3]
    mapped_observers.added_observers.assert_called_once(((1, 9), (3, 4)))


def test_map_str_list_to_lengths_remove_all():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = SequenceObservers(mapped)
    assert list(mapped) == [5, 6, 6]
    observable_list.clear()
    assert list(mapped) == []
    mapped_observers.removed_observers.assert_called_once(((0, 5), (1, 6), (2, 6)))


def test_map_str_list_to_lengths_get_item():
    observable_list = ObservableList(["apple", "banana", "cherry"])
    mapped = observable_list.map(lambda x: len(x))
    assert mapped[0] == 5
    assert mapped[1] == 6
    assert mapped[2] == 6
