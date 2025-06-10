from spellbind.bool_values import BoolConstant


def test_bool_constant_str():
    const = BoolConstant(True)
    assert str(const) == "True"

    const_false = BoolConstant(False)
    assert str(const_false) == "False"
