from conftest import NoParametersObserver, Call, OneParameterObserver
from spellbind.event import ValueEvent, Event


def test_adding_value_events_does_not_make_them_observed_until_derived_observed():
    event0 = ValueEvent[str]()
    event1 = ValueEvent[str]()
    combined_event = event0.or_value(event1)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()

    combined_event.observe(print)
    assert event0.is_observed()
    assert event1.is_observed()
    assert combined_event.is_observed()


def test_adding_value_events_observe_unobserve_makes_value_events_unobserved():
    event0 = ValueEvent[str]()
    event1 = ValueEvent[str]()
    combined_event = event0.or_value(event1)

    combined_event.observe(print)
    combined_event.unobserve(print)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()


def test_calling_either_value_event_triggers_combined_value_event():
    event0 = ValueEvent[str]()
    event1 = ValueEvent[str]()
    combined_event = event0.or_value(event1)

    observer = OneParameterObserver()
    combined_event.observe(observer)

    event0("foo")
    assert observer.calls == ["foo"]
    event1("bar")
    assert observer.calls == ["foo", "bar"]


def test_combine_value_event_with_event():
    event0 = ValueEvent[str]()
    event1 = Event()
    combined_event = event0 | event1

    observer = NoParametersObserver()
    combined_event.observe(observer)

    event0("foo")
    assert observer.calls == [Call()]
    event1()
    assert observer.calls == [Call(), Call()]
