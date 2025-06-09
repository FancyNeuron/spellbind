import pytest

from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver
from spellbind.event import Event


def test_event_initialization_empty_subscriptions():
    event = Event()
    assert event._subscriptions == []


def test_event_observe_mock_observer_adds_subscription():
    event = Event()
    observer = NoParametersObserver()

    event.observe(observer)

    assert event.is_observed(observer)


def test_event_observe_mock_observer_too_many_parameters_fails():
    event = Event()

    with pytest.raises(ValueError):
        event.observe(OneParameterObserver())


def test_event_unobserve_mock_observer_removes_subscription():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)

    event.unobserve(observer)

    assert not event.is_observed(observer)


def test_event_unobserve_nonexistent_mock_observer_fails():
    event = Event()

    with pytest.raises(ValueError):
        event.unobserve(NoParametersObserver())


def test_event_call_unobserved_mock_observer_not_invoked():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)
    event.unobserve(observer)

    event()

    observer.assert_not_called()


def test_event_call_invokes_all_mock_observers():
    event = Event()
    observer0 = NoParametersObserver()
    observer1 = NoParametersObserver()
    event.observe(observer0)
    event.observe(observer1)

    event()

    observer0.assert_called_once_with()
    observer1.assert_called_once_with()


def test_event_observe_mock_observer_with_default_parameter():
    event = Event()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event()

    observer.assert_called_once_with("default")


def test_event_call_with_no_observers():
    event = Event()
    event()


def test_event_observe_function_observer_with_default_parameter():
    event = Event()

    calls = []

    def observer_with_default(param="default"):
        calls.append(param)

    event.observe(observer_with_default)
    event()
    assert calls == ["default"]


def test_event_observe_lambda_observer():
    event = Event()
    calls = []

    event.observe(lambda: calls.append(True))
    event()

    assert calls == [True]
