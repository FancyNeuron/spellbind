from conftest import NoParametersObserver, Call, TwoParametersObserver, void_observer
from spellbind.event import Event, BiEvent
from spellbind.observables import combine_bi_observables


def test_adding_value_events_does_not_make_them_observed_until_derived_observed():
    event0 = BiEvent[str, str]()
    event1 = BiEvent[str, str]()
    combined_event = combine_bi_observables(event0, event1)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()

    combined_event.observe(void_observer)
    assert event0.is_observed()
    assert event1.is_observed()
    assert combined_event.is_observed()


def test_adding_value_events_observe_unobserve_makes_value_events_unobserved():
    event0 = BiEvent[str, str]()
    event1 = BiEvent[str, str]()
    combined_event = combine_bi_observables(event0, event1)

    combined_event.observe(void_observer)
    combined_event.unobserve(void_observer)

    assert not event0.is_observed()
    assert not event1.is_observed()
    assert not combined_event.is_observed()


def test_calling_either_value_event_triggers_combined_value_event():
    event0 = BiEvent[str, str]()
    event1 = BiEvent[str, str]()
    combined_event = combine_bi_observables(event0, event1)

    observer = TwoParametersObserver()
    combined_event.observe(observer)

    event0("foo", "bar")
    assert observer.calls == [("foo", "bar")]
    event1("lorem", "ipsum")
    assert observer.calls == [("foo", "bar"), ("lorem", "ipsum")]


def test_combine_value_event_with_event():
    event0 = BiEvent[str, str]()
    event1 = Event()
    combined_event = event0.or_observable(event1)

    observer = NoParametersObserver()
    combined_event.observe(observer)

    event0("foo", "bar")
    assert observer.calls == [Call()]
    event1()
    assert observer.calls == [Call(), Call()]
