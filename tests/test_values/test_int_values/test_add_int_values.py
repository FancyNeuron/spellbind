import gc

from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_add_int_values_values():
    v0 = IntVariable(1)
    v1 = IntVariable(2)
    v2 = v0 + v1
    assert v2.value == 3

    v0.value = 3
    assert v2.value == 5


def test_add_int_value_plus_int_values():
    v0 = IntVariable(1)
    v2 = v0 + 2
    assert v2.value == 3

    v0.value = 3
    assert v2.value == 5


def test_add_int_value_plus_float():
    v0 = IntVariable(3)
    v2 = v0 + 2.5
    assert v2.value == 5.5

    v0.value = 4
    assert v2.value == 6.5


def test_add_int_value_plus_float_value():
    v0 = IntVariable(3)
    v1 = FloatVariable(2.5)
    v2 = v0 + v1
    assert v2.value == 5.5

    v0.value = 4
    assert v2.value == 6.5


def test_add_int_plus_int_value():
    v1 = IntVariable(2)
    v2 = 3 + v1
    assert v2.value == 5

    v1.value = 4
    assert v2.value == 7


def test_add_float_plus_int_value():
    v1 = IntVariable(2)
    v2 = 3.5 + v1
    assert v2.value == 5.5

    v1.value = 4
    assert v2.value == 7.5


def test_add_int_values_keeps_reference():
    v0 = IntVariable(1)
    v1 = IntVariable(2)
    v2 = v0 + v1
    assert len(v0._on_change._subscriptions) == 1
    gc.collect()

    v0.value = 3
    v1.value = 4
    assert len(v0._on_change._subscriptions) == 1


def test_add_int_values_garbage_collected():
    v0 = IntVariable(1)
    v1 = IntVariable(2)
    v2 = v0 + v1
    assert len(v0._on_change._subscriptions) == 1
    assert len(v1._on_change._subscriptions) == 1
    v2 = None
    gc.collect()
    v0.value = 3  # trigger removal of weak references
    v1.value = 4  # trigger removal of weak references
    assert len(v0._on_change._subscriptions) == 0
    assert len(v1._on_change._subscriptions) == 0
