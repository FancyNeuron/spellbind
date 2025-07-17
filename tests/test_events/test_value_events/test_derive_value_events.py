from conftest import OneParameterObserver, TwoParametersObserver, ThreeParametersObserver
from spellbind.event import ValueEvent


def test_derive_one():
    event = ValueEvent[str]()
    derived = event.map(lambda s: len(s))
    observer = OneParameterObserver()
    derived.observe(observer)
    event("foo bar")
    event("ada lovelace")
    event("foo bar baz")
    assert observer.calls == [7, 12, 11]


def test_derive_one_predicate():
    event = ValueEvent[str]()
    derived = event.map(lambda s: len(s), predicate=lambda s: len(s) % 2 == 0)
    observer = OneParameterObserver()
    derived.observe(observer)
    event("foo bar")
    event("ada lovelace")
    event("foo bar baz")
    event("foobar")
    event("foobarbaz")
    assert observer.calls == [12, 6]


def test_derive_two():
    event = ValueEvent[str]()
    derived = event.map_to_two(lambda s: (s[0:len(s) // 2], s[len(s) // 2:]))
    observer = TwoParametersObserver()
    derived.observe(observer)
    event("f")
    event("oo")
    event("bar")
    event("foobar")
    assert observer.calls == [("", "f"), ("o", "o"), ("b", "ar"), ("foo", "bar")]


def test_derive_two_predicate():
    event = ValueEvent[str]()
    derived = event.map_to_two(lambda s: (s[0:len(s) // 2], s[len(s) // 2:]), predicate=lambda s: len(s) % 2 == 0)
    observer = TwoParametersObserver()
    derived.observe(observer)
    event("f")
    event("oo")
    event("bar")
    event("foobar")
    assert observer.calls == [("o", "o"), ("foo", "bar")]


def test_derive_three():
    event = ValueEvent[str]()
    derived = event.map_to_three(lambda s: (s[0:len(s) // 3], s[len(s) // 3:2 * len(s) // 3], s[2 * len(s) // 3:]))
    observer = ThreeParametersObserver()
    derived.observe(observer)
    event("foobar")
    event("foobarbaz")
    event("ada lovelace")
    assert observer.calls == [("fo", "ob", "ar"), ("foo", "bar", "baz"), ("ada ", "love", "lace")]


def test_derive_three_predicate():
    event = ValueEvent[str]()
    derived = event.map_to_three(lambda s: (s[0:len(s) // 3], s[len(s) // 3:2 * len(s) // 3], s[2 * len(s) // 3:]),
                                 predicate=lambda s: len(s) % 3 == 0)
    observer = ThreeParametersObserver()
    derived.observe(observer)
    event("foobar")
    event("foob")
    event("foobarbaz")
    event("adalovelace")
    event("ada lovelace")
    assert observer.calls == [("fo", "ob", "ar"), ("foo", "bar", "baz"), ("ada ", "love", "lace")]


def test_derive_many():
    event = ValueEvent[str]()
    derived = event.map_to_many(lambda s: s.split())
    observer = OneParameterObserver()
    derived.observe(observer)
    event("foobar")
    event("foo bar")
    event("ada lovelace")
    event("Lorem ipsum dolor sit amet consectetur adipiscing elit")
    assert observer.calls == [
        ["foobar", ],
        ["foo", "bar"],
        ["ada", "lovelace"],
        ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit"]
    ]


def test_derive_many_predicate():
    event = ValueEvent[str]()
    derived = event.map_to_many(lambda s: s.split(), predicate=lambda s: " " in s)
    observer = OneParameterObserver()
    derived.observe(observer)
    event("x")
    event("foobar")
    event("foo bar")
    event("ada lovelace")
    event("Lorem ipsum dolor sit amet consectetur adipiscing elit")
    event("Loremipsumdolorsitametconsecteturadipiscingelit")
    assert observer.calls == [
        ["foo", "bar"],
        ["ada", "lovelace"],
        ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit"]
    ]


def test_value_event_called_only_after_derived_observed():
    event = ValueEvent[int]()
    event_observer = OneParameterObserver()
    event.observe(event_observer)
    plus_one_calls = []

    def plus_one(value: int) -> int:
        plus_one_calls.append(value)
        return value + 1

    derived_event = event.map(plus_one)
    event(3)
    assert plus_one_calls == []
    assert event_observer.calls == [3]

    derived_observer = OneParameterObserver()
    derived_event.observe(derived_observer)

    event(5)
    assert plus_one_calls == [5]
    assert event_observer.calls == [3, 5]
    derived_observer.assert_called_once_with(6)


def test_value_event_called_only_after_derived_twice_observed():
    event = ValueEvent[int]()

    plus_one_calls = []

    def plus_one(value: int) -> int:
        plus_one_calls.append(value)
        return value + 1

    times_two_calls = []

    def times_two(value: int) -> int:
        times_two_calls.append(value)
        return value * 2

    derived_1 = event.map(plus_one)
    derived_2 = derived_1.map(times_two)
    event(3)
    assert plus_one_calls == []
    assert times_two_calls == []

    observer = OneParameterObserver()
    derived_2.observe(observer)
    event(5)
    assert plus_one_calls == [5]
    assert times_two_calls == [6]
    observer.assert_called_once_with(12)


def test_unobserve_derived_event_silences_makes_event_unobserved():
    event = ValueEvent[int]()
    observer = OneParameterObserver()
    derived_event = event.map(lambda x: x + 1)
    derived_event.observe(observer)
    assert event.is_observed()

    derived_event.unobserve(observer)
    assert not event.is_observed()
