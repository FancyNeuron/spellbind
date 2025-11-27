from conftest import OneParameterObserver
from spellbind.int_values import IntVariable, IntConstant


def test_constant_equals_constant():
    v0 = IntConstant(0)
    v1 = IntConstant(0)
    equals = v0.equals(v1)
    assert equals.value is True


def test_constant_does_not_equal_constant():
    v0 = IntConstant(0)
    v1 = IntConstant(1)
    equals = v0.equals(v1)
    assert equals.value is False


def test_equal_values_become_unequal():
    v = IntVariable(0)
    c = IntConstant(0)
    equals = v.equals(c)
    observer = OneParameterObserver()
    equals.observe(observer)
    assert equals.value is True
    v.value = 1
    assert equals.value is False
    observer.assert_called_once_with(False)


def test_unequal_values_become_equal():
    v = IntVariable(1)
    c = IntConstant(0)
    equals = v.equals(c)
    observer = OneParameterObserver()
    equals.observe(observer)
    assert equals.value is False
    v.value = 0
    assert equals.value is True
    observer.assert_called_once_with(True)


def test_become_unequal_and_equal_again():
    v = IntVariable(0)
    c = IntConstant(0)
    equals = v.equals(c)
    observer = OneParameterObserver()
    equals.observe(observer)
    assert equals.value is True
    v.value = 1
    assert equals.value is False
    v.value = 0
    assert equals.value is True
    assert observer.calls == [False, True]
