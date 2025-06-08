from pybind.str_values import StrVariable


def test_concatenate_str_values():
    variable0 = StrVariable("Hello")
    variable1 = StrVariable("World")

    concatenated = variable0 + variable1
    assert concatenated.value == "HelloWorld"

    variable0.value = "foo"
    variable1.value = "bar"

    assert concatenated.value == "foobar"
