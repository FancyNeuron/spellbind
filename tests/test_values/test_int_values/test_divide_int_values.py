from spellbind.float_values import FloatVariable
from spellbind.int_values import IntVariable


def test_truediv_int_values():
    v0 = IntVariable(10)
    v1 = IntVariable(4)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15
    assert v2.value == 3.75


def test_truediv_int_value_by_int():
    v0 = IntVariable(10)
    v2 = v0 / 4
    assert v2.value == 2.5

    v0.value = 15
    assert v2.value == 3.75


def test_truediv_int_value_by_float():
    v0 = IntVariable(10)
    v2 = v0 / 4.0
    assert v2.value == 2.5

    v0.value = 15
    assert v2.value == 3.75


def test_truediv_int_value_by_float_value():
    v0 = IntVariable(10)
    v1 = FloatVariable(4.0)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15
    assert v2.value == 3.75


def test_floordiv_int_values():
    v0 = IntVariable(10)
    v1 = IntVariable(3)
    v2 = v0 // v1
    assert v2.value == 3

    v0.value = 15
    assert v2.value == 5


def test_floordiv_int_value_by_int():
    v0 = IntVariable(10)
    v2 = v0 // 3
    assert v2.value == 3

    v0.value = 15
    assert v2.value == 5


def test_truediv_int_divided_by_int_value():
    v1 = IntVariable(4)
    v2 = 10 / v1
    assert v2.value == 2.5

    v1.value = 5
    assert v2.value == 2.0


def test_truediv_float_divided_by_int_value():
    v1 = IntVariable(4)
    v2 = 10.0 / v1
    assert v2.value == 2.5

    v1.value = 5
    assert v2.value == 2.0


def test_floordiv_int_divided_by_int_value():
    v1 = IntVariable(3)
    v2 = 10 // v1
    assert v2.value == 3

    v1.value = 4
    assert v2.value == 2
