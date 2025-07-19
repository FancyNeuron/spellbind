import gc

import pytest

from conftest import OneParameterObserver
from spellbind.observables import StrongSubscription, CallCountExceededError, StrongManyToOneSubscription, \
    WeakSubscription, DeadReferenceError, WeakManyToOneSubscription


def void_silent_chane(silent: bool):
    pass


def void_event():
    pass


def test_strong_subscription_match_observer():
    subscription = StrongSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.matches_observer(void_event)
    assert not subscription.matches_observer(lambda x: x)


def test_strong_subscriptions_call_increases_counter():
    subscription = StrongSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.call_counter == 0
    subscription("foobar")
    assert subscription.call_counter == 1
    subscription("foobar")
    assert subscription.call_counter == 2


def test_strong_subscriptions_raises_if_max_calls_exceeded():
    subscription = StrongSubscription(void_event, times=2, on_silent_change=void_silent_chane)
    assert subscription.max_call_count == 2
    subscription("foobar")
    with pytest.raises(CallCountExceededError):
        subscription("foobar")


def test_strong_subscriptions_calls_observable():
    calls = []
    subscription = StrongSubscription(lambda x: calls.append(x), times=None, on_silent_change=void_silent_chane)
    subscription("foobar")
    subscription("barfoo")
    assert calls == ["foobar", "barfoo"]


def test_strong_many_to_one_subscription_match_observer():
    subscription = StrongManyToOneSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.matches_observer(void_event)
    assert not subscription.matches_observer(lambda x: x)


def test_strong_many_to_one_subscriptions_raises_if_max_calls_exceeded():
    calls = []
    subscription = StrongManyToOneSubscription(lambda x: calls.append(x), times=2, on_silent_change=void_silent_chane)
    with pytest.raises(CallCountExceededError):
        subscription(("foobar", "barfoo", "Ada Lovelace"))
    assert calls == ["foobar", "barfoo"]


def test_strong_many_to_one_subscription_calls_observable():
    calls = []
    subscription = StrongManyToOneSubscription(lambda x: calls.append(x), times=None, on_silent_change=void_silent_chane)
    subscription(("foobar", "barfoo", "Ada Lovelace"))
    assert calls == ["foobar", "barfoo", "Ada Lovelace"]


def test_weak_subscription_match_observer():
    subscription = WeakSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.matches_observer(void_event)
    assert not subscription.matches_observer(lambda x: x)


def test_weak_subscriptions_call_increases_counter():
    subscription = WeakSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.call_counter == 0
    subscription("foobar")
    assert subscription.call_counter == 1
    subscription("foobar")
    assert subscription.call_counter == 2


def test_weak_subscriptions_raises_if_max_calls_exceeded():
    subscription = WeakSubscription(void_event, times=2, on_silent_change=void_silent_chane)
    assert subscription.max_call_count == 2
    subscription("foobar")
    with pytest.raises(CallCountExceededError):
        subscription("foobar")


def test_weak_subscription_garbage_collected():
    subscription = WeakSubscription(lambda x: print(x), times=None, on_silent_change=void_silent_chane)
    gc.collect()
    with pytest.raises(DeadReferenceError):
        subscription("foobar")


def test_weak_many_to_one_subscription_match_observer():
    subscription = WeakManyToOneSubscription(void_event, times=None, on_silent_change=void_silent_chane)
    assert subscription.matches_observer(void_event)
    assert not subscription.matches_observer(lambda x: x)


def test_weak_many_to_one_subscription_garbage_collected():
    subscription = WeakManyToOneSubscription(lambda x: print(x), times=None, on_silent_change=void_silent_chane)
    gc.collect()
    with pytest.raises(DeadReferenceError):
        subscription(("foobar", "barfoo", "Ada Lovelace"))


def test_weak_many_to_one_subscription_not_garbage_collected():
    calls = []

    def call(value):
        calls.append(value)

    subscription = WeakManyToOneSubscription(call, times=None, on_silent_change=void_silent_chane)
    gc.collect()
    subscription(("foobar", "barfoo", "Ada Lovelace"))
    assert calls == ["foobar", "barfoo", "Ada Lovelace"]


def test_weak_many_to_one_method_subscription_garbage_collected():
    observer = OneParameterObserver()

    subscription = WeakManyToOneSubscription(observer.__call__, times=None, on_silent_change=void_silent_chane)
    observer = None
    gc.collect()
    with pytest.raises(DeadReferenceError):
        subscription(("foobar", "barfoo", "Ada Lovelace"))


def test_weak_many_to_one_method_subscription_not_garbage_collected():
    observer = OneParameterObserver()

    subscription = WeakManyToOneSubscription(observer.__call__, times=None, on_silent_change=void_silent_chane)
    gc.collect()
    subscription(("foobar", "barfoo", "Ada Lovelace"))
    assert observer.calls == ["foobar", "barfoo", "Ada Lovelace"]
