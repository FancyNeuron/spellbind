from conftest import void_observer
from spellbind.values import SimpleVariable


def test_variable_is_not_observed():
    variable = SimpleVariable("test")
    assert not variable.is_observed()


def test_variable_is_observed():
    variable = SimpleVariable("test")
    variable.observe(void_observer)
    assert variable.is_observed()


def test_variable_is_observed_by_void_observer():
    variable = SimpleVariable("test")
    variable.observe(void_observer)
    assert variable.is_observed(void_observer)


def test_variable_is_not_observed_by_lambda():
    variable = SimpleVariable("test")
    variable.observe(void_observer)
    assert not variable.is_observed(lambda x: print(x))
