from conftest import OneParameterObserver, TwoParametersObserver, ThreeParametersObserver
from spellbind.event import BiEvent


def test_bi_event_merge():
    event = BiEvent[str, int]()
    merged = event.map_to_value_observable(lambda s, i: f"{s}-{i}")
    observer = OneParameterObserver()
    merged.observe(observer)
    event("foo", 1)
    event("bar", 2)
    event("baz", 3)
    assert observer.calls == ["foo-1", "bar-2", "baz-3"]


def test_bi_event_merge_predicate():
    event = BiEvent[str, int]()
    merged = event.map_to_value_observable(lambda s, i: f"{s}-{i}", predicate=lambda s, i: i % 2 == 0)
    observer = OneParameterObserver()
    merged.observe(observer)
    event("foo", 1)
    event("bar", 2)
    event("baz", 3)
    event("qux", 4)
    assert observer.calls == ["bar-2", "qux-4"]


def test_bi_event_map():
    event = BiEvent[str, int]()
    mapped = event.map_to_bi_observable(lambda s, i: (s.upper(), i * 2))
    observer = TwoParametersObserver()
    mapped.observe(observer)
    event("foo", 1)
    event("bar", 2)
    event("baz", 3)
    assert observer.calls == [("FOO", 2), ("BAR", 4), ("BAZ", 6)]


def test_bi_event_map_predicate():
    event = BiEvent[str, int]()
    mapped = event.map_to_bi_observable(lambda s, i: (s.upper(), i * 2), predicate=lambda s, i: i % 2 == 0)
    observer = TwoParametersObserver()
    mapped.observe(observer)
    event("foo", 1)
    event("bar", 2)
    event("baz", 3)
    event("qux", 4)
    assert observer.calls == [("BAR", 4), ("QUX", 8)]


def test_bi_event_split_to_three():
    event = BiEvent[str, int]()
    split = event.map_to_tri_observable(lambda s, i: (s[0], s[1:], i))
    observer = ThreeParametersObserver()
    split.observe(observer)
    event("foo", 1)
    event("bar", 2)
    event("baz", 3)
    assert observer.calls == [("f", "oo", 1), ("b", "ar", 2), ("b", "az", 3)]


def test_bi_event_split_to_three_predicate():
    event = BiEvent[str, int]()
    split = event.map_to_tri_observable(
        lambda s, i: (s[0], s[1:], i),
        predicate=lambda s, i: len(s) > 2
    )
    observer = ThreeParametersObserver()
    split.observe(observer)
    event("f", 1)
    event("foo", 2)
    event("ba", 3)
    event("baz", 4)
    assert observer.calls == [("f", "oo", 2), ("b", "az", 4)]


def test_bi_event_called_only_after_observed():
    event = BiEvent[str, int]()
    event_observer = TwoParametersObserver()
    event.observe(event_observer)
    transform_calls = []

    def transform(s: str, i: int) -> str:
        transform_calls.append((s, i))
        return f"{s}-{i}"

    merged_event = event.map_to_value_observable(transform)
    event("foo", 1)
    assert transform_calls == []
    assert event_observer.calls == [("foo", 1)]

    merged_observer = OneParameterObserver()
    merged_event.observe(merged_observer)

    event("bar", 2)
    assert transform_calls == [("bar", 2)]
    assert event_observer.calls == [("foo", 1), ("bar", 2)]
    merged_observer.assert_called_once_with("bar-2")


def test_unobserve_derived_bi_event():
    event = BiEvent[str, int]()
    observer = OneParameterObserver()
    merged_event = event.map_to_value_observable(lambda s, i: f"{s}-{i}")
    merged_event.observe(observer)
    assert event.is_observed()

    merged_event.unobserve(observer)
    assert not event.is_observed()


def test_bi_event_chained_transformations():
    event = BiEvent[str, int]()

    map_calls = []

    def map_fn(s: str, i: int) -> tuple[str, int]:
        map_calls.append((s, i))
        return s.upper(), i * 2

    merge_calls = []

    def merge_fn(s: str, i: int) -> str:
        merge_calls.append((s, i))
        return f"{s}:{i}"

    mapped = event.map_to_bi_observable(map_fn)
    merged = mapped.map_to_value_observable(merge_fn)

    observer = OneParameterObserver()
    merged.observe(observer)

    event("foo", 1)
    assert map_calls == [("foo", 1)]
    assert merge_calls == [("FOO", 2)]
    observer.assert_called_once_with("FOO:2")
