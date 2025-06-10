from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_multiply_int_value_times_int():
    v0 = IntVariable(3)
    v2 = v0 * 4
    assert v2.value == 12

    v0.value = 5
    assert v2.value == 20


def test_multiply_int_value_times_float():
    v0 = IntVariable(3)
    v2 = v0 * 2.5
    assert v2.value == 7.5

    v0.value = 4
    assert v2.value == 10.0


def test_multiply_int_value_times_float_value():
    v0 = IntVariable(3)
    v1 = FloatVariable(2.5)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4
    assert v2.value == 10.0


def test_multiply_int_times_int_value():
    v1 = IntVariable(4)
    v2 = 3 * v1
    assert v2.value == 12

    v1.value = 5
    assert v2.value == 15


def test_multiply_float_times_int_value():
    v1 = IntVariable(4)
    v2 = 2.5 * v1
    assert v2.value == 10.0

    v1.value = 6
    assert v2.value == 15.0


def test_multiply_int_values():
    v0 = IntVariable(3)
    v1 = IntVariable(4)
    v2 = v0 * v1
    assert v2.value == 12

    v0.value = 5
    assert v2.value == 20
