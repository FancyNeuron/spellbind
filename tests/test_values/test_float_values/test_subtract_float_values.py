from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_subtract_float_values():
    v0 = FloatVariable(5.5)
    v1 = FloatVariable(2.5)
    v2 = v0 - v1
    assert v2.value == 3.0

    v0.value = 10.5
    assert v2.value == 8.0


def test_subtract_float_value_minus_float():
    v0 = FloatVariable(5.5)
    v2 = v0 - 2.5
    assert v2.value == 3.0

    v0.value = 10.5
    assert v2.value == 8.0


def test_subtract_float_value_minus_int():
    v0 = FloatVariable(5.5)
    v2 = v0 - 2
    assert v2.value == 3.5

    v0.value = 10.5
    assert v2.value == 8.5


def test_subtract_float_value_minus_int_value():
    v0 = FloatVariable(5.5)
    v1 = IntVariable(2)
    v2 = v0 - v1
    assert v2.value == 3.5

    v0.value = 10.5
    assert v2.value == 8.5


def test_subtract_float_minus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 5.5 - v1
    assert v2.value == 3.0

    v1.value = 1.5
    assert v2.value == 4.0


def test_subtract_int_minus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 5 - v1
    assert v2.value == 2.5

    v1.value = 1.5
    assert v2.value == 3.5
