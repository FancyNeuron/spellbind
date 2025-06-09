from spellbind.float_values import FloatConstant


def test_float_constant_str():
    const = FloatConstant(3.14)
    assert str(const) == "3.14"
