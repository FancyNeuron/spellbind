from spellbind.int_values import IntVariable


def test_power_int_values():
    v0 = IntVariable(2)
    v1 = IntVariable(3)
    v2 = v0 ** v1
    assert v2.value == 8

    v0.value = 3
    assert v2.value == 27


def test_power_int_value_to_int():
    v0 = IntVariable(2)
    v2 = v0 ** 3
    assert v2.value == 8

    v0.value = 3
    assert v2.value == 27


def test_power_int_to_int_value():
    v1 = IntVariable(3)
    v2 = 2 ** v1
    assert v2.value == 8

    v1.value = 4
    assert v2.value == 16


# Modulo Tests
def test_modulo_int_values():
    v0 = IntVariable(10)
    v1 = IntVariable(3)
    v2 = v0 % v1
    assert v2.value == 1

    v0.value = 15
    assert v2.value == 0


def test_modulo_int_value_by_int():
    v0 = IntVariable(10)
    v2 = v0 % 3
    assert v2.value == 1

    v0.value = 15
    assert v2.value == 0


def test_modulo_int_by_int_value():
    v1 = IntVariable(3)
    v2 = 10 % v1
    assert v2.value == 1

    v1.value = 4
    assert v2.value == 2
