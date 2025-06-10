from spellbind.float_values import FloatConstant, MaxFloatValues, MinFloatValues
from spellbind.values import SimpleVariable


def test_float_constant_str():
    const = FloatConstant(3.14)
    assert str(const) == "3.14"


def test_max_float_values():
    a = SimpleVariable(10.5)
    b = SimpleVariable(20.3)
    c = SimpleVariable(5.7)

    max_val = MaxFloatValues(a, b, c)
    assert max_val.value == 20.3

    a.value = 30.1
    assert max_val.value == 30.1


def test_max_float_values_with_literals():
    a = SimpleVariable(10.5)

    max_val = MaxFloatValues(a, 25.7, 15.2)
    assert max_val.value == 25.7

    a.value = 30.1
    assert max_val.value == 30.1


def test_min_float_values():
    a = SimpleVariable(10.5)
    b = SimpleVariable(20.3)
    c = SimpleVariable(5.7)

    min_val = MinFloatValues(a, b, c)
    assert min_val.value == 5.7

    c.value = 2.1
    assert min_val.value == 2.1


def test_min_float_values_with_literals():
    a = SimpleVariable(10.5)

    min_val = MinFloatValues(a, 25.7, 15.2)
    assert min_val.value == 10.5

    a.value = 5.1
    assert min_val.value == 5.1
