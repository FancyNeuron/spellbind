import pytest

from spellbind.observable_sequences import empty_sequence
from spellbind.int_values import IntConstant
from spellbind.observables import VOID_VALUES_OBSERVABLE, VOID_VALUE_OBSERVABLE


def test_empty_sequence_str():
    empty_seq = empty_sequence()
    assert str(empty_seq) == "[]"


def test_empty_sequence_length():
    empty_seq = empty_sequence()
    assert len(empty_seq) == 0


def test_empty_sequence_length_value():
    empty_seq = empty_sequence()
    assert isinstance(empty_seq.length_value, IntConstant)
    assert empty_seq.length_value.value == 0


def test_empty_sequence_contains():
    empty_seq = empty_sequence()
    assert 1 not in empty_seq
    assert "test" not in empty_seq
    assert [] not in empty_seq
    assert {} not in empty_seq


def test_empty_sequence_iter():
    empty_seq = empty_sequence()
    assert list(empty_seq) == []


def test_empty_sequence_get_item_raises():
    empty_seq = empty_sequence()
    with pytest.raises(IndexError):
        empty_seq[0]


def test_empty_sequence_observers_are_void():
    empty_seq = empty_sequence()
    assert empty_seq.delta_observable is VOID_VALUES_OBSERVABLE
    assert empty_seq.on_change is VOID_VALUE_OBSERVABLE
