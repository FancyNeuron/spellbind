from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_multiply_float_values():
    v0 = FloatVariable(2.5)
    v1 = FloatVariable(3.0)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_multiply_float_value_times_float():
    v0 = FloatVariable(2.5)
    v2 = v0 * 3.0
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_multiply_float_value_times_int():
    v0 = FloatVariable(2.5)
    v2 = v0 * 3
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_multiply_float_value_times_int_value():
    v0 = FloatVariable(2.5)
    v1 = IntVariable(3)
    v2 = v0 * v1
    assert v2.value == 7.5

    v0.value = 4.0
    assert v2.value == 12.0


def test_multiply_float_times_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2.5 * v1
    assert v2.value == 7.5

    v1.value = 4.0
    assert v2.value == 10.0


def test_multiply_int_times_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2 * v1
    assert v2.value == 6.0

    v1.value = 4.0
    assert v2.value == 8.0
