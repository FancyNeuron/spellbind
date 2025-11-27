from conftest import OneParameterObserver
from spellbind.observable_sequences import ObservableList


def test_empty_is_empty():
    assert ObservableList([]).is_empty.value is True


def test_one_element_is_not_empty():
    assert ObservableList([1]).is_empty.value is False


def test_two_elements_is_not_empty():
    assert ObservableList([1, 2]).is_empty.value is False


def test_adding_one_element_to_empty_list_makes_it_not_empty():
    observable_list = ObservableList([])
    is_empty_value = observable_list.is_empty
    observer = OneParameterObserver()
    is_empty_value.observe(observer)
    observable_list.append(42)
    assert is_empty_value.value is False
    observer.assert_called_once_with(False)


def test_removing_only_element_makes_list_empty():
    observable_list = ObservableList([42])
    is_empty_value = observable_list.is_empty
    observer = OneParameterObserver()
    is_empty_value.observe(observer)
    del observable_list[0]
    assert is_empty_value.value is True
    observer.assert_called_once_with(True)


def test_removing_one_element_from_two_element_list_remains_non_empty():
    observable_list = ObservableList([1, 2])
    is_empty_value = observable_list.is_empty
    observer = OneParameterObserver()
    is_empty_value.observe(observer)
    del observable_list[0]
    assert is_empty_value.value is False
    observer.assert_not_called()


def test_add_and_remove_from_empty_list():
    observable_list = ObservableList([])
    is_empty_value = observable_list.is_empty
    observer = OneParameterObserver()
    is_empty_value.observe(observer)
    observable_list.append(1)
    assert is_empty_value.value is False
    observable_list.remove(1)
    assert is_empty_value.value is True
    assert observer.calls == [False, True]
