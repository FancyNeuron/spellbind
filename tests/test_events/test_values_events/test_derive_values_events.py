from conftest import OneParameterObserver, TwoParametersObserver, ThreeParametersObserver
from spellbind.event import ValuesEvent


def test_derive_one():
    event = ValuesEvent[str]()
    derived = event.map_to_one(" ".join)
    observer = OneParameterObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    assert observer.calls == ["foo bar ada lovelace"]


def test_derive_one_predicate():
    event = ValuesEvent[str]()
    derived = event.map_to_one(" ".join, predicate=lambda s: len(s) > 2)
    observer = OneParameterObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    event(["x", "y", "z"])
    event(["hello", "world"])
    assert observer.calls == ["foo bar ada lovelace", "x y z"]


def test_derive_two():
    event = ValuesEvent[str]()
    derived = event.map_to_two(lambda s: (" ".join(s), len(s)))
    observer = TwoParametersObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    assert observer.calls == [("foo bar ada lovelace", 4)]


def test_derive_two_predicate():
    event = ValuesEvent[str]()
    derived = event.map_to_two(lambda s: (" ".join(s), len(s)), predicate=lambda s: len(s) > 2)
    observer = TwoParametersObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    event(["x", "y", "z"])
    event(["hello", "world"])
    assert observer.calls == [("foo bar ada lovelace", 4), ("x y z", 3)]


def test_derive_three():
    event = ValuesEvent[str]()
    derived = event.map_to_three(lambda s: (" ".join(s), len(s), sum(len(s_s) for s_s in s) / len(s)))
    observer = ThreeParametersObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada"])
    event(["lorem", "ipsum", "dolor", "sitam"])
    assert observer.calls == [("foo bar ada", 3, 3.0), ("lorem ipsum dolor sitam", 4, 5.0)]


def test_derive_three_predicate():
    event = ValuesEvent[str]()
    derived = event.map_to_three(lambda s: (" ".join(s), len(s), sum(len(s_s) for s_s in s) / len(s)),
                                 predicate=lambda s: len(s) > 2)
    observer = ThreeParametersObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada"])
    event(["x", "y"])
    event(["lorem", "ipsum", "dolor", "sitam"])
    assert observer.calls == [("foo bar ada", 3, 3.0), ("lorem ipsum dolor sitam", 4, 5.0)]


def test_derive_many():
    event = ValuesEvent[str]()
    derived = event.map(lambda s: len(s))
    observer = OneParameterObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    event(["lorem", "ipsum", "dolor", "sit", "amet"])
    event(["x", "y", "z"])
    assert observer.calls == [(3, 3, 3, 8), (5, 5, 5, 3, 4), (1, 1, 1)]


def test_derive_many_predicate():
    event = ValuesEvent[str]()
    derived = event.map(lambda s: len(s), predicate=lambda s: len(s) > 3)
    observer = OneParameterObserver()
    derived.observe(observer)
    event(["foo", "bar", "ada", "lovelace"])
    event(["x", "y", "z", "a"])
    event(["lorem", "ipsum", "dolor", "sit", "amet"])
    assert observer.calls == [(8,), (), (5, 5, 5, 4)]


def test_values_event_called_only_after_derived_observed():
    event = ValuesEvent[int]()
    event_observer = OneParameterObserver()
    event.observe(event_observer)
    plus_one_calls = []

    def plus_one(values: int) -> int:
        plus_one_calls.append(values)
        return values + 1

    derived_event = event.map(plus_one)
    event([3, 4])
    assert plus_one_calls == []
    assert event_observer.calls == [[3, 4]]

    derived_observer = OneParameterObserver()
    derived_event.observe(derived_observer)

    event([5, 6])
    assert plus_one_calls == [5, 6]
    assert event_observer.calls == [[3, 4], [5, 6]]
    derived_observer.assert_called_once_with((6, 7))


def test_values_event_called_only_after_derived_twice_observed():
    event = ValuesEvent[int]()

    plus_one_calls = []

    def plus_one(values: int) -> int:
        plus_one_calls.append(values)
        return values + 1

    times_two_calls = []

    def times_two(values: int) -> int:
        times_two_calls.append(values)
        return values * 2

    derived_1 = event.map(plus_one)
    derived_2 = derived_1.map(times_two)

    event([3, 4])
    assert plus_one_calls == []
    assert times_two_calls == []

    observer = OneParameterObserver()
    derived_2.observe(observer)
    event([5, 6])
    assert plus_one_calls == [5, 6]
    assert times_two_calls == [6, 7]
    observer.assert_called_once_with((12, 14))


def test_unobserve_derived_event_silences_makes_event_unobserved():
    event = ValuesEvent[int]()
    observer = OneParameterObserver()
    derived_event = event.map(lambda x: x + 1)
    derived_event.observe(observer)
    assert event.is_observed()

    derived_event.unobserve(observer)
    assert not event.is_observed()
