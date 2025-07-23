from conftest import NoParametersObserver, Call, void_observer
from spellbind.event import Event
from spellbind.observables import Observable


def test_or_events_does_not_make_them_observed_until_derived_observed():
    event0 = Event()
    event1 = Event()
    combined_event = event0.or_observable(event1)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()

    combined_event.observe(void_observer)
    assert event0.is_observed()
    assert event1.is_observed()
    assert combined_event.is_observed()


def test_or_events_observe_unobserve_makes_events_unobserved():
    event0 = Event()
    event1 = Event()
    combined_event: Observable = event0.or_observable(event1)

    combined_event.observe(void_observer)
    combined_event.unobserve(void_observer)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()


def test_calling_either_event_triggers_combined_event():
    event0 = Event()
    event1 = Event()
    combined_event = event0.or_observable(event1)

    observer = NoParametersObserver()
    combined_event.observe(observer)

    event0()
    assert observer.calls == [Call()]
    event1()
    assert observer.calls == [Call(), Call()]
