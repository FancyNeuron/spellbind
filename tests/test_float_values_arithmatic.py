from pybind.float_values import FloatVariable
from pybind.int_values import IntVariable


# Addition Tests
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


# Subtraction Tests
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


# Multiplication Tests
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


# Division Tests
def test_truediv_float_values():
    v0 = FloatVariable(10.0)
    v1 = FloatVariable(4.0)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_value_by_float():
    v0 = FloatVariable(10.0)
    v2 = v0 / 4.0
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_value_by_int():
    v0 = FloatVariable(10.0)
    v2 = v0 / 4
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_value_by_int_value():
    v0 = FloatVariable(10.0)
    v1 = IntVariable(4)
    v2 = v0 / v1
    assert v2.value == 2.5

    v0.value = 15.0
    assert v2.value == 3.75


def test_truediv_float_divided_by_float_value():
    v1 = FloatVariable(4.0)
    v2 = 10.0 / v1
    assert v2.value == 2.5

    v1.value = 5.0
    assert v2.value == 2.0


def test_truediv_int_divided_by_float_value():
    v1 = FloatVariable(4.0)
    v2 = 10 / v1
    assert v2.value == 2.5

    v1.value = 5.0
    assert v2.value == 2.0


# Unary Minus Tests - Float
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
