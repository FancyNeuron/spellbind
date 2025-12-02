from conftest import ValueCollectionObservers, OneParameterObserver
from spellbind.actions import clear_action, SimpleRemoveOneAction, SimpleAddOneAction, SimpleOneElementChangedAction
from spellbind.observable_sequences import ObservableList
from spellbind.observable_collections import FilteredObservableBag


def test_initialize_empty():
    source = ObservableList()
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert len(filtered) == 0
    assert list(filtered) == []


def test_initialize_with_matching_items():
    source = ObservableList([1, 2, 3, 4, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]


def test_initialize_with_no_matching_items():
    source = ObservableList([1, 3, 5, 7])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert len(filtered) == 0
    assert list(filtered) == []


def test_initialize_with_duplicates():
    source = ObservableList([2, 2, 4, 2])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert len(filtered) == 4
    assert sorted(filtered) == [2, 2, 2, 4]


def test_contains_matching_item():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert 2 in filtered
    assert 4 in filtered


def test_does_not_contain_non_matching_item():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    assert 1 not in filtered
    assert 3 not in filtered


def test_append_matching_item():
    source = ObservableList([1, 2, 3])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.append(4)

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_added_calls(4)
    observers.assert_single_action(SimpleAddOneAction(4))


def test_append_non_matching_item():
    source = ObservableList([2, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.append(5)

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_append_duplicate_matching_item():
    source = ObservableList([2, 4, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.append(4)

    assert len(filtered) == 4
    assert sorted(filtered) == [2, 4, 4, 6]
    observers.assert_added_calls(4)
    observers.assert_single_action(SimpleAddOneAction(4))


def test_remove_matching_item():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.remove(2)

    assert len(filtered) == 1
    assert list(filtered) == [4]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_remove_non_matching_item():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.remove(1)

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_remove_duplicate_matching_item():
    source = ObservableList([2, 2, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    assert len(filtered) == 3

    source.remove(2)
    assert len(filtered) == 2
    assert 2 in filtered

    source.remove(2)
    assert len(filtered) == 1
    assert 2 not in filtered

    observers.assert_removed_calls(2, 2)
    observers.assert_actions(SimpleRemoveOneAction(2), SimpleRemoveOneAction(2))


def test_clear_source():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.clear()

    assert len(filtered) == 0
    assert list(filtered) == []
    observers.assert_removed_calls(2, 4)
    observers.assert_single_action(clear_action())


def test_clear_empty_source():
    source = ObservableList([1, 3, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.clear()

    assert len(filtered) == 0
    observers.assert_not_called()


def test_clear_filtered_empty():
    source = ObservableList()
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.clear()

    assert len(filtered) == 0
    observers.assert_not_called()


def test_length_value_updates():
    source = ObservableList([1, 2, 3])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)

    length_observer = OneParameterObserver()
    filtered.length_value.observe(length_observer)

    assert filtered.length_value.value == 1

    source.append(4)
    assert filtered.length_value.value == 2

    source.append(5)
    assert filtered.length_value.value == 2

    source.remove(2)
    assert filtered.length_value.value == 1

    assert length_observer.calls == [2, 1]


def test_multiple_operations():
    source = ObservableList([1, 2, 3, 4, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    assert sorted(filtered) == [2, 4]

    source.append(6)
    assert sorted(filtered) == [2, 4, 6]

    source.append(7)
    assert sorted(filtered) == [2, 4, 6]

    source.remove(2)
    assert sorted(filtered) == [4, 6]

    source.clear()
    assert list(filtered) == []

    observers.assert_calls((6, True), (2, False), (4, False), (6, False))
    observers.assert_actions(
        SimpleAddOneAction(6),
        SimpleRemoveOneAction(2),
        clear_action()
    )


def test_is_unobserved_initially():
    source = ObservableList([1, 2, 3])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)

    assert not filtered.on_change.is_observed()
    assert not filtered.delta_observable.is_observed()


def test_multiple_adds_and_removes_with_duplicates():
    source = ObservableList([2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    assert sorted(filtered) == [2, 4]
    assert len(filtered) == 2

    source.append(2)
    assert len(filtered) == 3
    assert sorted(filtered) == [2, 2, 4]

    source.append(6)
    assert len(filtered) == 4
    assert sorted(filtered) == [2, 2, 4, 6]

    source.remove(2)
    assert len(filtered) == 3
    assert 2 in filtered

    source.remove(2)
    assert len(filtered) == 2
    assert 2 not in filtered
    assert sorted(filtered) == [4, 6]

    observers.assert_calls((2, True), (6, True), (2, False), (2, False))
    observers.assert_actions(
        SimpleAddOneAction(2),
        SimpleAddOneAction(6),
        SimpleRemoveOneAction(2),
        SimpleRemoveOneAction(2)
    )


def test_setitem_matching_to_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[1] = 6

    assert len(filtered) == 2
    assert sorted(filtered) == [4, 6]
    observers.assert_calls((2, False), (6, True))
    observers.assert_single_action(SimpleOneElementChangedAction(old_item=2, new_item=6))


def test_setitem_matching_to_non_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[1] = 5

    assert len(filtered) == 1
    assert sorted(filtered) == [4]
    observers.assert_removed_calls(2)
    observers.assert_actions(SimpleRemoveOneAction(2))


def test_setitem_non_matching_to_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[0] = 6

    assert len(filtered) == 3
    assert sorted(filtered) == [2, 4, 6]
    observers.assert_added_calls(6)
    observers.assert_actions(SimpleAddOneAction(6))


def test_setitem_non_matching_to_non_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[0] = 5

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_setitem_to_duplicate():
    source = ObservableList([1, 2, 3, 4, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[1] = 4

    assert len(filtered) == 3
    assert sorted(filtered) == [4, 4, 6]
    observers.assert_calls((2, False), (4, True))
    observers.assert_single_action(SimpleOneElementChangedAction(old_item=2, new_item=4))


def test_extend_with_mixed_items():
    source = ObservableList([2, 3])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.extend([4, 5, 6, 7])

    assert len(filtered) == 3
    assert sorted(filtered) == [2, 4, 6]
    observers.assert_added_calls(4, 6)
    assert len(observers.on_change_observer.calls) == 1


def test_extend_with_only_non_matching():
    source = ObservableList([2, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.extend([1, 3, 5])

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_extend_with_duplicates():
    source = ObservableList([2, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.extend([2, 6, 2, 8])

    assert len(filtered) == 6
    assert sorted(filtered) == [2, 2, 2, 4, 6, 8]
    observers.assert_added_calls(2, 6, 2, 8)
    assert len(observers.on_change_observer.calls) == 1


def test_insert_matching_item():
    source = ObservableList([1, 3, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.insert(1, 4)

    assert len(filtered) == 1
    assert list(filtered) == [4]
    observers.assert_added_calls(4)
    observers.assert_single_action(SimpleAddOneAction(4))


def test_insert_non_matching_item():
    source = ObservableList([2, 4, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.insert(1, 3)

    assert len(filtered) == 3
    assert sorted(filtered) == [2, 4, 6]
    observers.assert_not_called()


def test_insert_duplicate_matching_item():
    source = ObservableList([2, 4, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.insert(1, 2)

    assert len(filtered) == 4
    assert sorted(filtered) == [2, 2, 4, 6]
    observers.assert_added_calls(2)
    observers.assert_single_action(SimpleAddOneAction(2))


def test_del_by_index_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    del source[1]

    assert len(filtered) == 1
    assert list(filtered) == [4]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_del_by_index_non_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    del source[0]

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_del_by_index_with_duplicates():
    source = ObservableList([2, 4, 2, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    del source[0]

    assert len(filtered) == 3
    assert sorted(filtered) == [2, 4, 6]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_del_by_slice():
    source = ObservableList([1, 2, 3, 4, 5, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    del source[1:4]

    assert len(filtered) == 1
    assert list(filtered) == [6]
    observers.assert_removed_calls(2, 4)
    assert len(observers.on_change_observer.calls) == 1


def test_del_by_slice_with_duplicates():
    source = ObservableList([2, 4, 2, 6, 2, 8])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    del source[1:4]

    assert len(filtered) == 3
    assert sorted(filtered) == [2, 2, 8]
    observers.assert_removed_calls(4, 2, 6)
    assert len(observers.on_change_observer.calls) == 1


def test_pop_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    popped = source.pop(3)

    assert popped == 4
    assert len(filtered) == 1
    assert sorted(filtered) == [2]
    observers.assert_removed_calls(4)
    observers.assert_single_action(SimpleRemoveOneAction(4))


def test_pop_non_matching():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    popped = source.pop(0)

    assert popped == 1
    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()


def test_pop_default():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    popped = source.pop()

    assert popped == 4
    assert len(filtered) == 1
    assert sorted(filtered) == [2]
    observers.assert_removed_calls(4)
    observers.assert_single_action(SimpleRemoveOneAction(4))


def test_pop_with_duplicates():
    source = ObservableList([2, 4, 2, 6])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    popped = source.pop(2)

    assert popped == 2
    assert len(filtered) == 3
    assert sorted(filtered) == [2, 4, 6]
    observers.assert_removed_calls(2)
    observers.assert_single_action(SimpleRemoveOneAction(2))


def test_slice_assignment_mixed():
    source = ObservableList([1, 2, 3, 4, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[1:4] = [6, 7, 8]

    assert len(filtered) == 2
    assert sorted(filtered) == [6, 8]
    observers.assert_calls((2, False), (6, True), (4, False), (8, True))
    assert len(observers.on_change_observer.calls) == 1


def test_slice_assignment_with_duplicates():
    source = ObservableList([1, 2, 3, 4, 5])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source[1:4] = [6, 6, 8]

    assert len(filtered) == 3
    assert sorted(filtered) == [6, 6, 8]
    observers.assert_calls((2, False), (6, True), (6, True), (4, False), (8, True))
    assert len(observers.on_change_observer.calls) == 1


def test_reverse():
    source = ObservableList([1, 2, 3, 4])
    filtered = FilteredObservableBag(source, lambda x: x % 2 == 0)
    observers = ValueCollectionObservers(filtered)

    source.reverse()

    assert len(filtered) == 2
    assert sorted(filtered) == [2, 4]
    observers.assert_not_called()
