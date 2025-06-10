from spellbind.str_values import StrConstant


def test_str_constant_str():
    const = StrConstant("hello")
    assert str(const) == "hello"
