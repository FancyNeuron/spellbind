from spellbind.int_values import IntConstant, MaxIntValues, MinIntValues
from spellbind.values import SimpleVariable


def test_int_constant_str():
    const = IntConstant(42)
    assert str(const) == "42"


def test_max_int_values():
    a = SimpleVariable(10)
    b = SimpleVariable(20)
    c = SimpleVariable(5)

    max_val = MaxIntValues(a, b, c)
    assert max_val.value == 20

    a.value = 30
    assert max_val.value == 30


def test_max_int_values_with_literals():
    a = SimpleVariable(10)

    max_val = MaxIntValues(a, 25, 15)
    assert max_val.value == 25

    a.value = 30
    assert max_val.value == 30


def test_min_int_values():
    a = SimpleVariable(10)
    b = SimpleVariable(20)
    c = SimpleVariable(5)

    min_val = MinIntValues(a, b, c)
    assert min_val.value == 5

    c.value = 2
    assert min_val.value == 2


def test_min_int_values_with_literals():
    a = SimpleVariable(10)

    min_val = MinIntValues(a, 25, 15)
    assert min_val.value == 10

    a.value = 5
    assert min_val.value == 5
