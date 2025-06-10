from spellbind.int_values import IntVariable


def test_negate_int_value():
    v0 = IntVariable(5)
    v1 = -v0
    assert v1.value == -5

    v0.value = -3
    assert v1.value == 3


def test_negate_int_value_zero():
    v0 = IntVariable(0)
    v1 = -v0
    assert v1.value == 0

    v0.value = 7
    assert v1.value == -7


def test_abs_int_value_positive():
    v0 = IntVariable(5)
    v1 = abs(v0)
    assert v1.value == 5

    v0.value = 10
    assert v1.value == 10


def test_abs_int_value_negative():
    v0 = IntVariable(-5)
    v1 = abs(v0)
    assert v1.value == 5

    v0.value = -10
    assert v1.value == 10


def test_abs_int_value_zero():
    v0 = IntVariable(0)
    v1 = abs(v0)
    assert v1.value == 0

    v0.value = -7
    assert v1.value == 7
