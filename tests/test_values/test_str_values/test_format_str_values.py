import pytest

from conftest import OneParameterObserver
from spellbind.str_values import StrVariable, StrConstant


def test_format_variable_with_str():
    variable = StrVariable("Hello {name}")
    formatted = variable.format(name="World")
    assert formatted.value == "Hello World"


def test_format_variable_with_variable():
    variable = StrVariable("Hello {name}")
    name_variable = StrVariable("World")
    formatted = variable.format(name=name_variable)
    assert formatted.value == "Hello World"


def test_format_variable_with_constant():
    variable = StrVariable("Hello {name}")
    name_constant = StrConstant.of("World")
    formatted = variable.format(name=name_constant)
    assert formatted.value == "Hello World"


def test_format_constant_with_str():
    constant = StrConstant.of("Hello {name}")
    formatted = constant.format(name="World")
    assert formatted.value == "Hello World"


def test_format_constant_with_variable():
    constant = StrConstant.of("Hello {name}")
    name_variable = StrVariable("World")
    formatted = constant.format(name=name_variable)
    assert formatted.value == "Hello World"


def test_format_constant_with_constant():
    constant = StrConstant.of("Hello {name}")
    name_constant = StrConstant.of("World")
    formatted = constant.format(name=name_constant)
    assert formatted.value == "Hello World"


def test_format_variable_with_str_change_base():
    variable = StrVariable("Hello {name}")
    formatted = variable.format(name="World")
    observer = OneParameterObserver()
    formatted.observe(observer)
    assert formatted.value == "Hello World"

    variable.value = "Hi {name}"
    assert formatted.value == "Hi World"
    observer.assert_called_once_with("Hi World")


def test_format_const_with_variable_change_option():
    constant = StrConstant.of("Hello {name}")
    name_variable = StrVariable("World")
    formatted = constant.format(name=name_variable)
    observer = OneParameterObserver()
    formatted.observe(observer)
    assert formatted.value == "Hello World"

    name_variable.value = "Universe"
    assert formatted.value == "Hello Universe"
    observer.assert_called_once_with("Hello Universe")


def test_format_constant_with_non_existing_key_raises():
    constant = StrConstant.of("Hello {name}")
    with pytest.raises(KeyError):
        constant.format(age=30)


def test_format_variable_with_str_base_changes_to_invalid_key_does_not_raise():
    variable = StrVariable("Hello {name}")
    formatted = variable.format(name="World")
    observer = OneParameterObserver()
    formatted.observe(observer)
    assert formatted.value == "Hello World"

    variable.value = "Hello {namee}"
    assert formatted.value == "Hello {namee}"
    observer.assert_called_once_with("Hello {namee}")


def test_format_constant_with_two_strs():
    constant = StrConstant.of("Coordinates: ({x}, {y})")
    formatted = constant.format(x="10", y="20")
    assert formatted.value == "Coordinates: (10, 20)"


def test_format_constant_with_two_variables_change_both():
    constant = StrConstant.of("Coordinates: ({x}, {y})")
    x_var = StrVariable("10")
    y_var = StrVariable("20")
    formatted = constant.format(x=x_var, y=y_var)
    observer = OneParameterObserver()
    formatted.observe(observer)
    assert formatted.value == "Coordinates: (10, 20)"

    x_var.value = "15"
    assert formatted.value == "Coordinates: (15, 20)"

    y_var.value = "25"
    assert formatted.value == "Coordinates: (15, 25)"
    assert observer.calls == ["Coordinates: (15, 20)", "Coordinates: (15, 25)"]
