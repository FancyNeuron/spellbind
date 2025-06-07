import pytest
from unittest.mock import Mock

from pybind.event import Event


class Observer(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NoParametersObserver(Observer):
    def __call__(self):
        super().__call__()


class OneParameterObserver(Observer):
    def __call__(self, param0):
        super().__call__(param0)


class OneDefaultParameterObserver(Observer):
    def __call__(self, param0="default"):
        super().__call__(param0=param0)


def test_event_initialization():
    event = Event()
    assert event._observers == []


def test_mock_observe_adds_observer():
    event = Event()
    observer = NoParametersObserver()
    observer.__name__ = "test_observer"

    event.observe(observer)

    assert observer in event._observers


def test_mock_observe_validates_parameter_count():
    event = Event()

    with pytest.raises(ValueError):
        event.observe(OneParameterObserver())


def test_mock_unobserve_removes_observer():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)

    event.unobserve(observer)

    assert observer not in event._observers


def test_mock_unobserve_nonexistent_observer_raises():
    event = Event()

    with pytest.raises(ValueError):
        event.unobserve(NoParametersObserver())


def test_mock_unobserved_observer_not_called():
    event = Event()
    observer = NoParametersObserver()
    event.observe(observer)
    event.unobserve(observer)

    event()

    observer.assert_not_called()


def test_mock_call_invokes_all_observers():
    event = Event()
    observer0 = NoParametersObserver()
    observer1 = NoParametersObserver()
    event.observe(observer0)
    event.observe(observer1)

    event()

    observer0.assert_called_once_with()
    observer1.assert_called_once_with()


def test_mock_observer_with_default_parameter():
    event = Event()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event()

    observer.assert_called_once_with(param0="default")


def test_call_with_no_observers():
    event = Event()
    event()


def test_function_observer_with_default_parameter():
    event = Event()

    calls = []

    def observer_with_default(param="default"):
        calls.append(param)

    event.observe(observer_with_default)
    event()
    assert calls == ["default"]


def test_lambda_observer():
    event = Event()
    calls = []

    event.observe(lambda: calls.append(True))
    event()

    assert calls == [True]
