import gc

import pytest

from conftest import NoParametersObserver, OneParameterObserver
from pybind.event import Event


def test_weak_observe_adds_observer():
    event = Event()
    observer = NoParametersObserver()

    event.weak_observe(observer)

    assert event.is_observed(observer)


def test_weak_observe_validates_parameter_count():
    event = Event()

    with pytest.raises(ValueError):
        event.weak_observe(OneParameterObserver())


def test_weak_observe_calls_observer():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event()

    observer.assert_called_once_with()


def test_weak_observe_unobserve_removes_observer():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_weak_observe_unobserve_twice_removes_observer():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)
    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_weak_observe_twice_unobserve_once_still_observer():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)
    event.weak_observe(observer)

    event.unobserve(observer)

    assert event.is_observed(observer)


def test_weak_observe_auto_cleanup():
    event = Event()
    observer = NoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0


def test_weak_observe_with_function():
    event = Event()
    calls = []

    def observer():
        calls.append(True)

    event.weak_observe(observer)
    event()

    assert calls == [True]


def test_mixed_weak_and_strong_observers():
    event = Event()
    strong_observer = NoParametersObserver()
    weak_observer = NoParametersObserver()

    event.observe(strong_observer)
    event.weak_observe(weak_observer)

    event()

    strong_observer.assert_called_once_with()
    weak_observer.assert_called_once_with()


def test_weak_observe_method_auto_cleanup():
    event = Event()

    observer = NoParametersObserver()
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0


def test_weak_observe_method_before_cleanup():
    event = Event()

    observer = NoParametersObserver()
    event.weak_observe(observer)

    event()

    observer.assert_called_once_with()
    assert len(event._subscriptions) == 1


def test_weak_lambda_cleaned_immediately_observer():
    event = Event()
    calls = []

    event.weak_observe(lambda: calls.append(True))
    event()

    assert calls == []


def test_weak_lambda_cleanup():
    event = Event()
    calls = []

    observer = lambda: calls.append(True)
    event.weak_observe(observer)

    del observer
    gc.collect()

    event()

    assert len(event._subscriptions) == 0
    assert calls == []


def test_weak_lambda_unobserve():
    event = Event()
    calls = []

    observer = lambda: calls.append(True)
    event.weak_observe(observer)
    event.unobserve(observer)

    event()

    assert calls == []
    assert not event.is_observed(observer)


def test_call_order_mixed_weak_strong():
    event = Event()
    calls = []

    observer0 = lambda: calls.append("test 0")
    observer1 = lambda: calls.append("test 1")
    observer2 = lambda: calls.append("test 2")
    observer3 = lambda: calls.append("test 3")

    event.observe(observer0)
    event.weak_observe(observer1)
    event.observe(observer2)
    event.weak_observe(observer3)

    event()

    assert calls == ["test 0", "test 1", "test 2", "test 3"]
