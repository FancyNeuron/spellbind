from spellbind.int_values import IntConstant


def test_int_constant_str():
    const = IntConstant(42)
    assert str(const) == "42"
