import pytest

from spellbind.str_values import StrVariable, ManyStrsToStrValue, StrConstant


def test_concatenate_str_values():
    variable0 = StrVariable("Hello")
    variable1 = StrVariable("World")

    concatenated = variable0 + variable1
    assert concatenated.value == "HelloWorld"

    variable0.value = "foo"
    variable1.value = "bar"

    assert concatenated.value == "foobar"


def test_concatenate_str_value_literal_str_value():
    first_name = StrVariable("Ada")
    last_name = StrVariable("Lovelace")
    full_name = first_name + " " + last_name

    assert full_name.value == "Ada Lovelace"


def test_concatenate_str_value_literal():
    first_name = StrVariable("Ada")
    full_name = first_name + " Lovelace"

    assert full_name.value == "Ada Lovelace"


def test_concatenate_literal_str_value():
    last_name = StrVariable("Lovelace")
    full_name = "Ada " + last_name

    assert full_name.value == "Ada Lovelace"


def test_concatenate_many_str_values_waterfall_style_are_combined():
    v0 = StrVariable("foo")
    v1 = StrVariable("bar")
    v2 = StrVariable("hello")
    v3 = StrVariable("world")

    v4 = v0 + v1 + v2 + v3
    assert v4.value == "foobarhelloworld"

    assert isinstance(v4, ManyStrsToStrValue)
    assert v4._input_values == (v0, v1, v2, v3)


def test_concatenate_many_str_values_grouped_are_combined():
    v0 = StrVariable("foo")
    v1 = StrVariable("bar")
    v2 = StrVariable("hello")
    v3 = StrVariable("world")

    v4 = (v0 + v1) + (v2 + v3)
    assert v4.value == "foobarhelloworld"

    assert isinstance(v4, ManyStrsToStrValue)
    assert v4._input_values == (v0, v1, v2, v3)


@pytest.mark.parametrize("v0, v1", [
    (StrConstant("foo"), "bar"),
    ("foo", StrConstant("bar")),
    (StrConstant("foo"), StrConstant("bar")),
])
def test_concatenate_str_constants_is_constant(v0, v1):
    v2 = v0 + v1
    assert v2.constant_value_or_raise == "foobar"
