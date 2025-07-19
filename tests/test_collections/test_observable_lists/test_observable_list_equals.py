import pytest

from spellbind.int_collections import ObservableIntList, IntValueList
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import ObservableList
from spellbind.str_collections import StrValueList
from spellbind.str_values import StrVariable


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList, StrValueList])
def test_equal_int_not_implemented(constructor):
    observable_list = constructor()
    result = observable_list.__eq__(42)
    assert result is NotImplemented


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_equal_list_with_variable(constructor):
    value = IntVariable(3)
    observable_list_0 = constructor([1, 2, value])
    observable_list_1 = constructor([1, 2, value])
    assert observable_list_0.__eq__(observable_list_1)


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_equal_list_literal_is_not_variable(constructor):
    value = IntVariable(3)
    observable_list = constructor([1, 2, value])
    assert not observable_list == [1, 2, 3]


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_equal_list_literals_are_not_equal(constructor):
    observable_list = constructor([1, 2, 3])
    assert observable_list != [1, 2, 4]


def test_equal_str_list_literals_are_not_equal():
    observable_list = StrValueList(["foo", "bar", "baz"])
    assert observable_list != ["foo", "bar", "qux"]


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_equal_list_different_variables_are_not_equal(constructor):
    observable_list = constructor([1, 2, IntVariable(3)])
    assert observable_list != [1, 2, IntVariable(3)]


def test_equal_str_list_different_variables_are_not_equal():
    observable_list = StrValueList(["foo", "bar", StrVariable("baz")])
    assert observable_list != ["foo", "bar", StrVariable("baz")]


@pytest.mark.parametrize("constructor", [ObservableList, ObservableIntList, IntValueList])
def test_equal_list_literals_unequal_lengths(constructor):
    observable_list = constructor([1, 2, 3])
    assert observable_list != [1, 2, 3, 4]


def test_equal_str_list_literals_unequal_lengths():
    observable_list = StrValueList(["foo", "bar", "baz"])
    assert observable_list != ["foo", "bar", "baz", "qux"]
