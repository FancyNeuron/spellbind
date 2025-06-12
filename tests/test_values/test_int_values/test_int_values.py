from spellbind.int_values import IntConstant, MaxIntValues, MinIntValues, IntVariable
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


def test_clamp_int_values_in_range():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15


def test_clamp_int_values_below_min():
    value = IntVariable(5)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 10


def test_clamp_int_values_above_max():
    value = IntVariable(25)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 20


def test_clamp_int_values_with_literals_in_range():
    value = IntVariable(15)

    clamped = value.clamp(10, 20)
    assert clamped.value == 15


def test_clamp_int_values_with_literals_below_min():
    value = IntVariable(5)

    clamped = value.clamp(10, 20)
    assert clamped.value == 10


def test_clamp_int_values_with_literals_above_max():
    value = IntVariable(25)

    clamped = value.clamp(10, 20)
    assert clamped.value == 20


def test_clamp_int_values_reactive_value_changes():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15

    value.value = 5
    assert clamped.value == 10

    value.value = 25
    assert clamped.value == 20

    value.value = 12
    assert clamped.value == 12


def test_clamp_int_values_reactive_bounds_changes():
    value = IntVariable(15)
    min_val = IntVariable(10)
    max_val = IntVariable(20)

    clamped = value.clamp(min_val, max_val)
    assert clamped.value == 15

    min_val.value = 18
    assert clamped.value == 18

    min_val.value = 11
    assert clamped.value == 15

    max_val.value = 12
    assert clamped.value == 12


def test_derived_int_values_map_to_list():
    value0 = IntConstant(2)
    value1 = IntConstant(3)
    added = value0 + value1
    mapped_value = added.map(lambda x: ["foo"]*x)

    assert mapped_value.value == ["foo", "foo", "foo", "foo", "foo"]


def test_int_const_repr():
    const = IntConstant(42)
    assert repr(const) == "IntConstant(42)"
