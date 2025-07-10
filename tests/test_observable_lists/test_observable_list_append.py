from conftest import OneParameterObserver
from spellbind.collections import ObservableList


def test_append_notifies():
    observable_list = ObservableList([1, 2, 3])
    observer = OneParameterObserver()
    observable_list.added_observable.observe_single(observer)
    observable_list.append(4)
    assert observable_list == [1, 2, 3, 4]
    assert observable_list.length_value.value == 4
    observer.assert_called_once_with(4)


def test_append_length_already_set_but_notifies_after():
    observable_list = ObservableList([1, 2, 3])
    events = []

    def assert_list_length():
        events.append("added")
        assert len(observable_list) == 4
        assert observable_list.length_value.value == 4
    observable_list.added_observable.observe(assert_list_length)
    observable_list.length_value.observe(lambda i: events.append(f"length set to {i}"))
    observable_list.append(4)
    assert events == ["added", "length set to 4"]
