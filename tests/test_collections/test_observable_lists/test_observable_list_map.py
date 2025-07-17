import pytest

from conftest import ValueSequenceObservers, assert_length_changed_during_action_events_but_notifies_after
from spellbind.actions import reverse_action, InsertAllAction, \
    SimpleRemoveAtIndexAction, SimpleInsertAction, \
    SimpleSetAtIndexAction, SimpleInsertAllAction, SimpleRemoveAtIndicesAction, SimpleExtendAction, clear_action
from spellbind.sequences import ObservableList, ValueList


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_lengths_set_item_unobserved(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert list(mapped) == [5, 6, 3]
    observable_list[1] = "blueberry"
    assert list(mapped) == [5, 9, 3]


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_append(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.append("blueberry")
    assert list(mapped) == [5, 6, 3, 9]
    mapped_observers.assert_added_calls((3, 9))
    mapped_observers.assert_single_action(SimpleInsertAction(3, 9))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_clear(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.clear()
    assert list(mapped) == []
    mapped_observers.assert_removed_calls((0, 5), (0, 6), (0, 3))
    mapped_observers.assert_single_action(clear_action())


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_del_item(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    del observable_list[1]
    assert list(mapped) == [5, 3]
    mapped_observers.assert_removed_calls((1, 6))
    mapped_observers.assert_single_action(SimpleRemoveAtIndexAction(1, 6))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_del_slice(constructor):
    observable_list = constructor(["apple", "banana", "fig", "plum"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3, 4]
    del observable_list[1:3]
    assert list(mapped) == [5, 4]
    mapped_observers.assert_removed_calls((1, 6), (1, 3))
    mapped_observers.assert_single_action(SimpleRemoveAtIndicesAction(((1, 6), (2, 3))))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_extend(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.extend(["blueberry", "apricot"])
    assert list(mapped) == [5, 6, 3, 9, 7]
    mapped_observers.assert_added_calls((3, 9), (4, 7))
    mapped_observers.assert_single_action(SimpleExtendAction(3, (9, 7)))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_insert(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.insert(1, "blueberry")
    assert list(mapped) == [5, 9, 6, 3]
    mapped_observers.assert_added_calls((1, 9))
    mapped_observers.assert_single_action(SimpleInsertAction(1, 9))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_insert_all(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.insert_all([(1, "blueberry"), (3, "apricot")])
    assert list(mapped) == [5, 9, 6, 3, 7]
    mapped_observers.assert_added_calls((1, 9), (4, 7))
    mapped_observers.assert_single_action(SimpleInsertAllAction(((1, 9), (3, 7))))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_insert_all_out_of_order(constructor):
    observable_list = constructor(["apple", "banana", "fig", "plum"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3, 4]
    observable_list.insert_all([(3, "apricot"), (1, "blueberry")])
    assert list(mapped) == [5, 9, 6, 3, 7, 4]
    mapped_observers.assert_added_calls((1, 9), (4, 7))
    mapped_observers.assert_single_action(SimpleInsertAllAction(((1, 9), (3, 7))))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_pop(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    popped_item = observable_list.pop(1)
    assert popped_item == "banana"
    assert list(mapped) == [5, 3]
    mapped_observers.assert_removed_calls((1, 6))
    mapped_observers.assert_single_action(SimpleRemoveAtIndexAction(1, 6))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_remove(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.remove("banana")
    assert list(mapped) == [5, 3]
    mapped_observers.assert_removed_calls((1, 6))
    mapped_observers.assert_single_action(SimpleRemoveAtIndexAction(1, 6))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_reverse(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list.reverse()
    assert list(mapped) == [3, 6, 5]
    mapped_observers.assert_calls((0, 5, False), (0, 6, False), (0, 3, False), (0, 3, True), (1, 6, True), (2, 5, True))
    mapped_observers.assert_single_action(reverse_action())


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_set_item(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    mapped_observers = ValueSequenceObservers(mapped)
    assert list(mapped) == [5, 6, 3]
    observable_list[1] = "blueberry"
    assert list(mapped) == [5, 9, 3]
    mapped_observers.assert_calls((1, 6, False), (1, 9, True))
    mapped_observers.assert_single_action(SimpleSetAtIndexAction(1, old_item=6, new_item=9))


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_str_list_to_lengths_get_item(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    assert mapped[0] == 5
    assert mapped[1] == 6
    assert mapped[2] == 3


@pytest.mark.parametrize("constructor", [ObservableList, ValueList])
def test_map_length_already_set_but_notifies_after(constructor):
    observable_list = constructor(["apple", "banana", "fig"])
    mapped = observable_list.map(lambda x: len(x))
    with assert_length_changed_during_action_events_but_notifies_after(mapped, 5):
        observable_list.extend(("blueberry", "apricot"))
