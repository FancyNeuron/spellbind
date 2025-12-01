import pytest

from conftest import ValueSequenceObservers, values_factories
from spellbind.actions import SimpleSliceSetAction, SimpleSetAtIndicesAction, SimpleSetAtIndexAction
from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.observable_sequences import ObservableList


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_observable_list_set_item_unobserved(constructor):
    observable_list = constructor([1, 2, 3])
    observable_list[1] = 4
    assert observable_list == [1, 4, 3]
    assert observable_list.length_value.value == 3


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_item_slice_unobserved(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5])
    observable_list[1:4] = values_factory(6, 7, 8)
    assert observable_list == [1, 6, 7, 8, 5]
    assert observable_list.length_value.value == 5


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_observable_list_set_item_notifies(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1] = 4
    assert observable_list == [1, 4, 3]
    assert observable_list.length_value.value == 3
    observers.assert_calls((1, 2, False), (1, 4, True))
    observers.assert_single_action(SimpleSetAtIndexAction(index=1, old_item=2, new_item=4))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_observable_list_set_item_negative_index(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[-1] = 4
    assert observable_list == [1, 2, 4]
    assert observable_list.length_value.value == 3
    observers.assert_calls((-1, 3, False), (-1, 4, True))
    observers.assert_single_action(SimpleSetAtIndexAction(index=-1, old_item=3, new_item=4))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_observable_list_set_item_out_of_range(constructor):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    with pytest.raises(IndexError):
        observable_list[3] = 4
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_list(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:4] = values_factory(6, 7, 8)
    assert observable_list == [1, 6, 7, 8, 5]
    assert observable_list.length_value.value == 5
    observers.assert_calls((1, 2, False), (1, 6, True), (2, 3, False), (2, 7, True), (3, 4, False), (3, 8, True))
    observers.assert_single_action(SimpleSetAtIndicesAction(indices_with_new_and_old=((1, 6, 2), (2, 7, 3), (3, 8, 4))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_partially_outside_list(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:4] = values_factory(4, 5)
    assert observable_list == [1, 4, 5]
    assert observable_list.length_value.value == 3
    observers.assert_calls((1, 2, False), (1, 4, True), (2, 3, False), (2, 5, True))
    observers.assert_single_action(SimpleSetAtIndicesAction(indices_with_new_and_old=((1, 4, 2), (2, 5, 3))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_remove_three_add_one(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:4] = values_factory(6)
    assert observable_list == [1, 6, 5]
    assert observable_list.length_value.value == 3
    observers.assert_calls((1, 2, False), (1, 3, False), (1, 4, False), (1, 6, True))
    observers.assert_single_action(SimpleSliceSetAction(indices=(1, 2, 3), new_items=(6,), old_items=(2, 3, 4)))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_end_smaller_than_start(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[2:1] = values_factory(4, 5, 6)
    assert observable_list == [1, 2, 4, 5, 6, 3]
    assert observable_list.length_value.value == 6
    observers.assert_calls((2, 4, True), (3, 5, True), (4, 6, True))
    observers.assert_single_action(SimpleSliceSetAction(indices=(2,), new_items=(4, 5, 6), old_items=()))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_empty(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:1] = values_factory(4, 5)
    assert observable_list == [1, 4, 5, 2, 3]
    assert observable_list.length_value.value == 5
    observers.assert_calls((1, 4, True), (2, 5, True))
    observers.assert_single_action(SimpleSliceSetAction(indices=(1,), new_items=(4, 5), old_items=()))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_one_to_neg_one_same_size(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:-1] = values_factory(6, 7, 8)
    assert observable_list == [1, 6, 7, 8, 5]
    assert observable_list.length_value.value == 5
    observers.assert_calls((1, 2, False), (1, 6, True), (2, 3, False), (2, 7, True), (3, 4, False), (3, 8, True))
    observers.assert_single_action(SimpleSetAtIndicesAction(indices_with_new_and_old=((1, 6, 2), (2, 7, 3), (3, 8, 4))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_one_to_neg_one_smaller_size(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:-1] = values_factory(6, 8)
    assert observable_list == [1, 6, 8, 5]
    assert observable_list.length_value.value == 4
    observers.assert_calls((1, 2, False), (1, 3, False), (1, 4, False), (1, 6, True), (2, 8, True))
    observers.assert_single_action(SimpleSliceSetAction(indices=(1, 2, 3), new_items=(6, 8), old_items=(2, 3, 4)))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_step_two(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5, 6])
    observers = ValueSequenceObservers(observable_list)
    observable_list[::2] = values_factory(7, 8, 9)
    assert observable_list == [7, 2, 8, 4, 9, 6]
    assert observable_list.length_value.value == 6
    observers.assert_calls((0, 1, False), (0, 7, True), (2, 3, False), (2, 8, True), (4, 5, False), (4, 9, True))
    observers.assert_single_action(SimpleSetAtIndicesAction(indices_with_new_and_old=((0, 7, 1), (2, 8, 3), (4, 9, 5))))


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_slice_step_two_smaller_size_raises(constructor, values_factory):
    observable_list = constructor([1, 2, 3, 4, 5, 6])
    observers = ValueSequenceObservers(observable_list)
    with pytest.raises(ValueError):
        observable_list[::2] = values_factory(7, 8)
    assert observable_list == [1, 2, 3, 4, 5, 6]
    assert observable_list.length_value.value == 6
    observers.assert_not_called()


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
@pytest.mark.parametrize("values_factory", values_factories())
def test_observable_list_set_empty_slice_no_values(constructor, values_factory):
    observable_list = constructor([1, 2, 3])
    observers = ValueSequenceObservers(observable_list)
    observable_list[1:1] = values_factory()
    assert observable_list == [1, 2, 3]
    assert observable_list.length_value.value == 3
    observers.assert_not_called()
