from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


# Power Tests
def test_power_float_values():
    v0 = FloatVariable(2.0)
    v1 = FloatVariable(3.0)
    v2 = v0 ** v1
    assert v2.value == 8.0

    v0.value = 3.0
    assert v2.value == 27.0


def test_power_float_value_to_float():
    v0 = FloatVariable(2.0)
    v2 = v0 ** 3.0
    assert v2.value == 8.0

    v0.value = 3.0
    assert v2.value == 27.0


def test_power_float_value_to_int():
    v0 = FloatVariable(2.5)
    v2 = v0 ** 2
    assert v2.value == 6.25

    v0.value = 3.0
    assert v2.value == 9.0


def test_power_float_value_to_int_value():
    v0 = FloatVariable(2.0)
    v1 = IntVariable(3)
    v2 = v0 ** v1
    assert v2.value == 8.0

    v0.value = 3.0
    assert v2.value == 27.0


def test_power_float_to_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2.0 ** v1
    assert v2.value == 8.0

    v1.value = 4.0
    assert v2.value == 16.0


def test_power_int_to_float_value():
    v1 = FloatVariable(3.0)
    v2 = 2 ** v1
    assert v2.value == 8.0

    v1.value = 4.0
    assert v2.value == 16.0


# Modulo Tests
def test_modulo_float_values():
    v0 = FloatVariable(10.5)
    v1 = FloatVariable(3.0)
    v2 = v0 % v1
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_float():
    v0 = FloatVariable(10.5)
    v2 = v0 % 3.0
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_int():
    v0 = FloatVariable(10.5)
    v2 = v0 % 3
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_value_by_int_value():
    v0 = FloatVariable(10.5)
    v1 = IntVariable(3)
    v2 = v0 % v1
    assert v2.value == 1.5

    v0.value = 15.5
    assert v2.value == 0.5


def test_modulo_float_by_float_value():
    v1 = FloatVariable(3.0)
    v2 = 10.5 % v1
    assert v2.value == 1.5

    v1.value = 4.0
    assert v2.value == 2.5


def test_modulo_int_by_float_value():
    v1 = FloatVariable(3.0)
    v2 = 10 % v1
    assert v2.value == 1.0

    v1.value = 4.0
    assert v2.value == 2.0
