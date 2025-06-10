from spellbind.str_values import StrVariable


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
