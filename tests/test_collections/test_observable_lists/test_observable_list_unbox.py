from conftest import ValueSequenceObservers
from spellbind.int_collections import IntValueList
from spellbind.int_values import IntVariable
from spellbind.observable_sequences import SimpleValueChangedMultipleTimesAction


def test_unbox_value_list():
    variable = IntVariable(3)
    observable_list = IntValueList([1, 2, variable])
    unboxed = observable_list.unboxed
    assert unboxed == [1, 2, 3]
    observers = ValueSequenceObservers(unboxed)
    variable.value = 4
    assert unboxed == [1, 2, 4]
    observers.assert_calls((3, False), (4, True))
    observers.assert_actions(SimpleValueChangedMultipleTimesAction(new_item=4, old_item=3, count=1))


def test_unbox_value_cached():
    observable_list = IntValueList([1, 2, 3])
    unboxed_0 = observable_list.unboxed
    unboxed_1 = observable_list.unboxed
    assert unboxed_0 is unboxed_1


def test_unbox_value_list_get_item():
    variable = IntVariable(3)
    observable_list = IntValueList([1, 2, variable])
    unboxed = observable_list.unboxed
    assert unboxed[0] == 1
    assert unboxed[1] == 2
    assert unboxed[2] == 3
    variable.value = 4
    assert unboxed[2] == 4


def test_unbox_value_list_get_slice():
    variable = IntVariable(3)
    observable_list = IntValueList([1, 2, variable])
    unboxed = observable_list.unboxed
    assert unboxed[0:2] == [1, 2]
    assert unboxed[1:3] == [2, 3]
    variable.value = 4
    assert unboxed[1:3] == [2, 4]


def test_unbox_value_list_str():
    variable = IntVariable(3)
    observable_list = IntValueList([1, 2, variable])
    unboxed = observable_list.unboxed
    assert str(unboxed) == "[1, 2, 3]"
    variable.value = 4
    assert str(unboxed) == "[1, 2, 4]"
