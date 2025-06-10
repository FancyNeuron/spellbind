from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_add_float_values():
    v0 = FloatVariable(1.5)
    v1 = FloatVariable(2.5)
    v2 = v0 + v1
    assert v2.value == 4.0

    v0.value = 3.5
    assert v2.value == 6.0


def test_add_float_value_plus_float():
    v0 = FloatVariable(1.5)
    v2 = v0 + 2.5
    assert v2.value == 4.0

    v0.value = 3.5
    assert v2.value == 6.0


def test_add_float_value_plus_int():
    v0 = FloatVariable(1.5)
    v2 = v0 + 2
    assert v2.value == 3.5

    v0.value = 3.5
    assert v2.value == 5.5


def test_add_float_value_plus_int_value():
    v0 = FloatVariable(1.5)
    v1 = IntVariable(2)
    v2 = v0 + v1
    assert v2.value == 3.5

    v0.value = 3.5
    assert v2.value == 5.5


def test_add_float_plus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 1.5 + v1
    assert v2.value == 4.0

    v1.value = 3.5
    assert v2.value == 5.0


def test_add_int_plus_float_value():
    v1 = FloatVariable(2.5)
    v2 = 2 + v1
    assert v2.value == 4.5

    v1.value = 3.5
    assert v2.value == 5.5
