import pytest
from pybind.event import TriEvent
from conftest import NoParametersObserver, OneParameterObserver, OneDefaultParameterObserver, \
    OneRequiredOneDefaultParameterObserver, TwoParametersObserver, TwoDefaultParametersObserver, \
    ThreeParametersObserver, ThreeDefaultParametersObserver, TwoRequiredOneDefaultParameterObserver


def test_tri_event_observe_and_call_no_parameters_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = NoParametersObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with()


def test_tri_event_observe_and_call_one_parameter_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = OneParameterObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value")


def test_tri_event_observe_and_call_one_default_parameter_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = OneDefaultParameterObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value")


def test_tri_event_observe_and_call_one_required_one_default_parameter_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = OneRequiredOneDefaultParameterObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42)


def test_tri_event_observe_and_call_two_parameters_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = TwoParametersObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42)


def test_tri_event_observe_and_call_two_required_one_default_parameter_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = TwoRequiredOneDefaultParameterObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42, True)


def test_tri_event_observe_and_call_three_parameters_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    event.observe(observer)
    event("test_value", 42, True)

    observer.assert_called_once_with("test_value", 42, True)


def test_tri_event_unobserve_mock_observer():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    event.observe(observer)
    event("test0", 0, False)
    event.unobserve(observer)
    event("test1", 1, True)

    observer.assert_called_once_with("test0", 0, False)


def test_tri_event_multiple_mock_observers():
    event = TriEvent[str, int, bool]()
    observer0 = NoParametersObserver()
    observer1 = OneParameterObserver()
    observer2 = TwoParametersObserver()
    observer3 = ThreeParametersObserver()

    event.observe(observer0)
    event.observe(observer1)
    event.observe(observer2)
    event.observe(observer3)
    event("hello", 123, False)

    observer0.assert_called_once_with()
    observer1.assert_called_once_with("hello")
    observer2.assert_called_once_with("hello", 123)
    observer3.assert_called_once_with("hello", 123, False)


def test_tri_event_function_observer_with_too_many_parameters():
    event = TriEvent[str, int, bool]()

    def bad_observer(param0, param1, param2, param3):
        pass

    with pytest.raises(ValueError):
        event.observe(bad_observer)


def test_tri_event_observe_and_call_lambda_no_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    event.observe(lambda: calls.append(True))
    event("test_value", 42, False)

    assert calls == [True]


def test_tri_event_observe_and_call_lambda_one_parameter():
    event = TriEvent[str, int, bool]()
    calls = []

    event.observe(lambda value0: calls.append(value0))
    event("test_value", 42, False)

    assert calls == ["test_value"]


def test_tri_event_observe_and_call_lambda_two_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    event.observe(lambda value0, value1: calls.append((value0, value1)))
    event("test_value", 42, False)

    assert calls == [("test_value", 42)]


def test_tri_event_observe_and_call_lambda_three_parameters():
    event = TriEvent[str, int, bool]()
    calls = []

    event.observe(lambda value0, value1, value2: calls.append((value0, value1, value2)))
    event("test_value", 42, False)

    assert calls == [("test_value", 42, False)]


def test_tri_event_unobserve_lambda():
    event = TriEvent[str, int, bool]()
    calls = []
    observer = lambda value0, value1, value2: calls.append((value0, value1, value2))

    event.observe(observer)
    event("test0", 0, False)
    event.unobserve(observer)
    event("test1", 1, True)

    assert calls == [("test0", 0, False)]


def test_tri_event_lambda_with_too_many_parameters():
    event = TriEvent[str, int, bool]()

    with pytest.raises(ValueError):
        event.observe(lambda param0, param1, param2, param3: None)


def test_tri_event_call_with_one_parameter():
    event = TriEvent[str, int, bool]()

    with pytest.raises(TypeError):
        event("param0")


def test_tri_event_call_with_two_parameters():
    event = TriEvent[str, int, bool]()

    with pytest.raises(TypeError):
        event("param0", 42)


def test_tri_event_call_with_four_parameters():
    event = TriEvent[str, int, bool]()

    with pytest.raises(TypeError):
        event("param0", 42, True, "param3")


def test_tri_event_unobserve_non_existent_observer():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    with pytest.raises(ValueError):
        event.unobserve(observer)


def test_tri_event_observe_same_observer_multiple_times():
    event = TriEvent[str, int, bool]()
    observer = ThreeParametersObserver()

    event.observe(observer)
    event.observe(observer)
    event("test", 42, True)

    assert observer.call_count == 2
    observer.assert_called_with("test", 42, True)


def test_tri_event_call_with_no_observers():
    event = TriEvent[str, int, bool]()
    event("test_value", 42, False)  # Should not raise


def test_tri_event_observers_called_in_order():
    event = TriEvent[str, int, bool]()
    call_order = []

    event.observe(lambda value0, value1, value2: call_order.append("first"))
    event.observe(lambda value0, value1, value2: call_order.append("second"))
    event.observe(lambda value0, value1, value2: call_order.append("third"))

    event("test", 42, False)

    assert call_order == ["first", "second", "third"]


def test_tri_event_call_with_none_values():
    event = TriEvent[str | None, int | None, bool | None]()
    observer = ThreeParametersObserver()

    event.observe(observer)
    event(None, None, None)

    observer.assert_called_once_with(None, None, None)
