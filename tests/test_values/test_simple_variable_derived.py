import pytest

from spellbind.values import SimpleVariable, Constant


def test_simple_variable_derived_from_empty():
    variable = SimpleVariable("test")

    assert variable.derived_from == frozenset()


def test_simple_variable_derived_from_bound():
    variable = SimpleVariable("test")
    constant = Constant("bound")

    variable.bind(constant)

    assert variable.derived_from == frozenset()


def test_simple_variable_deep_derived_from_empty():
    variable = SimpleVariable("test")

    assert list(variable.deep_derived_from) == []


def test_simple_variable_deep_derived_from_single_level():
    variable = SimpleVariable("test")
    constant = Constant("bound")

    variable.bind(constant)

    assert list(variable.deep_derived_from) == []


def test_simple_variable_deep_derived_from_two_levels():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    constant = Constant("bound")

    variable2.bind(constant)
    variable1.bind(variable2)

    dependencies = list(variable1.deep_derived_from)
    assert len(dependencies) == 1
    assert variable2 in dependencies


def test_simple_variable_deep_derived_from_three_levels():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    variable3 = SimpleVariable("test3")
    constant = Constant("bound")

    variable3.bind(constant)
    variable2.bind(variable3)
    variable1.bind(variable2)

    dependencies = list(variable1.deep_derived_from)
    assert len(dependencies) == 2
    assert variable2 in dependencies
    assert variable3 in dependencies


def test_simple_variable_deep_derived_from_circular_two_variables():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")

    variable1.bind(variable2)

    with pytest.raises(RecursionError):
        variable2.bind(variable1)


def test_simple_variable_deep_derived_from_circular_three_variables():
    variable1 = SimpleVariable("test1")
    variable2 = SimpleVariable("test2")
    variable3 = SimpleVariable("test3")

    variable1.bind(variable2)
    variable2.bind(variable3)

    with pytest.raises(RecursionError):
        variable3.bind(variable1)


def test_simple_variable_deep_derived_from_diamond_pattern():
    variable_top = SimpleVariable("top")
    variable_left = SimpleVariable("left")
    variable_right = SimpleVariable("right")
    variable_bottom = SimpleVariable("bottom")

    variable_left.bind(variable_top)
    variable_right.bind(variable_top)
    variable_bottom.bind(variable_left)
    variable_bottom.bind(variable_right, already_bound_ok=True)

    dependencies = list(variable_bottom.deep_derived_from)
    assert len(dependencies) == 2
    assert variable_right in dependencies
    assert variable_top in dependencies
