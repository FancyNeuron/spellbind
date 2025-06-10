from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_subtract_int_values():
    v0 = IntVariable(5)
    v1 = IntVariable(2)
    v2 = v0 - v1
    assert v2.value == 3

    v0.value = 10
    assert v2.value == 8


def test_subtract_int_value_minus_int():
    v0 = IntVariable(5)
    v2 = v0 - 2
    assert v2.value == 3

    v0.value = 10
    assert v2.value == 8


def test_subtract_int_value_minus_float():
    v0 = IntVariable(5)
    v2 = v0 - 2.5
    assert v2.value == 2.5

    v0.value = 10
    assert v2.value == 7.5


def test_subtract_int_value_minus_float_value():
    v0 = IntVariable(5)
    v1 = FloatVariable(2.5)
    v2 = v0 - v1
    assert v2.value == 2.5

    v0.value = 10
    assert v2.value == 7.5


def test_subtract_int_minus_int_value():
    v1 = IntVariable(2)
    v2 = 5 - v1
    assert v2.value == 3

    v1.value = 3
    assert v2.value == 2


def test_subtract_float_minus_int_value():
    v1 = IntVariable(2)
    v2 = 5.5 - v1
    assert v2.value == 3.5

    v1.value = 3
    assert v2.value == 2.5
