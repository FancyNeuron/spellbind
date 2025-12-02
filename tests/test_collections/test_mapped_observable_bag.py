from conftest import ValueCollectionObservers, OneParameterObserver
from spellbind.actions import clear_action, SimpleRemoveOneAction, SimpleAddOneAction, SimpleOneElementChangedAction
from spellbind.observable_sequences import ObservableList
from spellbind.observable_collections import MappedObservableBag


def test_initialize_empty():
    source = ObservableList()
    mapped = MappedObservableBag(source, lambda x: x * 2)
    assert len(mapped) == 0
    assert list(mapped) == []


def test_initialize_with_items():
    source = ObservableList([1, 2, 3, 4, 5])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    assert len(mapped) == 5
    assert sorted(mapped) == [2, 4, 6, 8, 10]


def test_initialize_with_duplicates():
    source = ObservableList([1, 2, 1, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    assert len(mapped) == 4
    assert sorted(mapped) == [2, 2, 4, 6]


def test_initialize_with_transform_to_string():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: f"item_{x}")
    assert len(mapped) == 3
    assert sorted(mapped) == ["item_1", "item_2", "item_3"]


def test_contains_mapped_item():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    assert 2 in mapped
    assert 4 in mapped
    assert 6 in mapped
    assert 8 in mapped


def test_does_not_contain_unmapped_item():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    assert 1 not in mapped
    assert 3 not in mapped
    assert 5 not in mapped


def test_append_item():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.append(4)

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 4, 6, 8]
    observers.assert_added_calls(8)
    observers.assert_single_action(SimpleAddOneAction(8))


def test_append_duplicate_item():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.append(2)

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 4, 4, 6]
    observers.assert_added_calls(4)
    observers.assert_single_action(SimpleAddOneAction(4))


def test_append_multiple_that_map_to_same():
    source = ObservableList([1, 2])
    mapped = MappedObservableBag(source, lambda x: x // 2)
    observers = ValueCollectionObservers(mapped)

    source.append(3)

    assert len(mapped) == 3
    assert sorted(mapped) == [0, 1, 1]
    observers.assert_added_calls(1)
    observers.assert_single_action(SimpleAddOneAction(1))


def test_remove_item():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.remove(2)

    assert len(mapped) == 3
    assert sorted(mapped) == [2, 6, 8]
    observers.assert_removed_calls(4)
    observers.assert_single_action(SimpleRemoveOneAction(4))


def test_remove_duplicate_item():
    source = ObservableList([1, 2, 1, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 2, 4, 6]

    source.remove(1)
    assert len(mapped) == 3
    assert 2 in mapped

    source.remove(1)
    assert len(mapped) == 2
    assert 2 not in mapped

    observers.assert_removed_calls(2, 2)
    observers.assert_actions(SimpleRemoveOneAction(2), SimpleRemoveOneAction(2))


def test_clear_source():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.clear()

    assert len(mapped) == 0
    assert list(mapped) == []
    observers.assert_removed_calls(2, 4, 6, 8)
    observers.assert_single_action(clear_action())


def test_clear_empty_source():
    source = ObservableList()
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.clear()

    assert len(mapped) == 0
    observers.assert_not_called()


def test_length_value_updates():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)

    length_observer = OneParameterObserver()
    mapped.length_value.observe(length_observer)

    assert mapped.length_value.value == 3

    source.append(4)
    assert mapped.length_value.value == 4

    source.remove(2)
    assert mapped.length_value.value == 3

    assert length_observer.calls == [4, 3]


def test_multiple_operations():
    source = ObservableList([1, 2, 3, 4, 5])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    assert sorted(mapped) == [2, 4, 6, 8, 10]

    source.append(6)
    assert sorted(mapped) == [2, 4, 6, 8, 10, 12]

    source.remove(2)
    assert sorted(mapped) == [2, 6, 8, 10, 12]

    source.clear()
    assert list(mapped) == []

    observers.assert_calls((12, True), (4, False), (2, False), (6, False), (8, False), (10, False), (12, False))
    observers.assert_actions(
        SimpleAddOneAction(12),
        SimpleRemoveOneAction(4),
        clear_action()
    )


def test_is_unobserved_initially():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)

    assert not mapped.on_change.is_observed()
    assert not mapped.delta_observable.is_observed()


def test_multiple_adds_and_removes_with_duplicates():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    assert sorted(mapped) == [2, 4, 6]
    assert len(mapped) == 3

    source.append(1)
    assert len(mapped) == 4
    assert sorted(mapped) == [2, 2, 4, 6]

    source.append(4)
    assert len(mapped) == 5
    assert sorted(mapped) == [2, 2, 4, 6, 8]

    source.remove(1)
    assert len(mapped) == 4
    assert 2 in mapped

    source.remove(1)
    assert len(mapped) == 3
    assert 2 not in mapped
    assert sorted(mapped) == [4, 6, 8]

    observers.assert_calls((2, True), (8, True), (2, False), (2, False))
    observers.assert_actions(
        SimpleAddOneAction(2),
        SimpleAddOneAction(8),
        SimpleRemoveOneAction(2),
        SimpleRemoveOneAction(2)
    )


def test_setitem():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source[1] = 5

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 6, 8, 10]
    observers.assert_calls((4, False), (10, True))
    observers.assert_single_action(SimpleOneElementChangedAction(old_item=4, new_item=10))


def test_setitem_to_duplicate():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source[1] = 1

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 2, 6, 8]
    observers.assert_calls((4, False), (2, True))
    observers.assert_single_action(SimpleOneElementChangedAction(old_item=4, new_item=2))


def test_extend_with_items():
    source = ObservableList([1, 2])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.extend([3, 4, 5])

    assert len(mapped) == 5
    assert sorted(mapped) == [2, 4, 6, 8, 10]
    observers.assert_added_calls(6, 8, 10)
    assert len(observers.on_change_observer.calls) == 1


def test_extend_with_duplicates():
    source = ObservableList([1, 2])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.extend([1, 3, 1, 4])

    assert len(mapped) == 6
    assert sorted(mapped) == [2, 2, 2, 4, 6, 8]
    observers.assert_added_calls(2, 6, 2, 8)
    assert len(observers.on_change_observer.calls) == 1


def test_insert_item():
    source = ObservableList([1, 3, 5])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.insert(1, 2)

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 4, 6, 10]
    observers.assert_added_calls(4)
    observers.assert_single_action(SimpleAddOneAction(4))


def test_insert_duplicate_item():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.insert(1, 1)

    assert len(mapped) == 4
    assert sorted(mapped) == [2, 2, 4, 6]
    observers.assert_added_calls(2)
    observers.assert_single_action(SimpleAddOneAction(2))


def test_del_by_index():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    del source[1]

    assert len(mapped) == 3
    assert sorted(mapped) == [2, 6, 8]
    observers.assert_removed_calls(4)
    observers.assert_single_action(SimpleRemoveOneAction(4))


def test_del_by_index_with_duplicates():
    source = ObservableList([1, 2, 1, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    del source[0]

    assert len(mapped) == 3
    assert sorted(mapped) == [2, 4, 6]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_del_by_slice():
    source = ObservableList([1, 2, 3, 4, 5, 6])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    del source[1:4]

    assert len(mapped) == 3
    assert sorted(mapped) == [2, 10, 12]
    observers.assert_removed_calls(4, 6, 8)
    assert len(observers.on_change_observer.calls) == 1


def test_del_by_slice_with_duplicates():
    source = ObservableList([1, 2, 1, 3, 1, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    del source[1:4]

    assert len(mapped) == 3
    assert sorted(mapped) == [2, 2, 8]
    observers.assert_removed_calls(4, 2, 6)
    assert len(observers.on_change_observer.calls) == 1


def test_pop():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    popped = source.pop(2)

    assert popped == 3
    assert len(mapped) == 3
    assert sorted(mapped) == [2, 4, 8]
    observers.assert_removed_calls(6)
    observers.assert_single_action(SimpleRemoveOneAction(6))


def test_pop_default():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    popped = source.pop()

    assert popped == 4
    assert len(mapped) == 3
    assert sorted(mapped) == [2, 4, 6]
    observers.assert_removed_calls(8)
    observers.assert_single_action(SimpleRemoveOneAction(8))


def test_pop_with_duplicates():
    source = ObservableList([1, 2, 1, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    popped = source.pop(0)

    assert popped == 1
    assert len(mapped) == 3
    assert 2 in mapped
    assert sorted(mapped) == [2, 4, 6]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_slice_assignment():
    source = ObservableList([1, 2, 3, 4, 5])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source[1:3] = [10, 20]

    assert len(mapped) == 5
    assert sorted(mapped) == [2, 8, 10, 20, 40]
    assert len(observers.delta_observer.calls) == 4
    assert len(observers.on_change_observer.calls) == 1


def test_slice_assignment_with_duplicates():
    source = ObservableList([1, 2, 3, 1, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source[1:3] = [1, 1]

    assert len(mapped) == 5
    assert sorted(mapped) == [2, 2, 2, 2, 8]
    assert len(observers.delta_observer.calls) == 4
    assert len(observers.on_change_observer.calls) == 1


def test_reverse():
    source = ObservableList([1, 2, 3, 4])
    mapped = MappedObservableBag(source, lambda x: x * 2)
    observers = ValueCollectionObservers(mapped)

    source.reverse()

    assert sorted(mapped) == [2, 4, 6, 8]
    observers.assert_not_called()


def test_transform_produces_same_values():
    source = ObservableList([1, 2, 3, 4, 5])
    mapped = MappedObservableBag(source, lambda x: x // 2)

    assert len(mapped) == 5
    assert sorted(mapped) == [0, 1, 1, 2, 2]

    observers = ValueCollectionObservers(mapped)

    source.remove(3)
    assert sorted(mapped) == [0, 1, 2, 2]
    observers.assert_removed_calls(1)


def test_repr():
    source = ObservableList([1, 2, 3])
    mapped = MappedObservableBag(source, lambda x: x * 2)

    repr_str = repr(mapped)
    assert "MappedObservableBag" in repr_str
