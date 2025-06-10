from spellbind.float_values import FloatVariable


def test_negate_float_value():
    v0 = FloatVariable(5.5)
    v1 = -v0
    assert v1.value == -5.5

    v0.value = -3.2
    assert v1.value == 3.2


def test_negate_float_value_zero():
    v0 = FloatVariable(0.0)
    v1 = -v0
    assert v1.value == 0.0

    v0.value = 7.8
    assert v1.value == -7.8


def test_abs_float_value_positive():
    v0 = FloatVariable(5.5)
    v1 = abs(v0)
    assert v1.value == 5.5

    v0.value = 10.8
    assert v1.value == 10.8


def test_abs_float_value_negative():
    v0 = FloatVariable(-5.5)
    v1 = abs(v0)
    assert v1.value == 5.5

    v0.value = -10.8
    assert v1.value == 10.8


def test_abs_float_value_zero():
    v0 = FloatVariable(0.0)
    v1 = abs(v0)
    assert v1.value == 0.0

    v0.value = -7.2
    assert v1.value == 7.2
