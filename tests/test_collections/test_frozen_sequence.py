import pytest

from spellbind.observable_sequences import FrozenObservableSequence, ObservableList, StaticObservableSequence


def test_initialize_frozen_sequence_empty_str():
    sequence = StaticObservableSequence()
    assert str(sequence) == "[]"


def test_initialize_frozen_sequence_empty_is_empty():
    sequence = StaticObservableSequence()
    assert len(sequence) == 0
    assert sequence.length_value.value == 0
    assert sequence.length_value.constant_value_or_raise == 0
    assert list(sequence) == []


def test_initialize_frozen_sequence_empty_observers_not_observed():
    sequence = StaticObservableSequence()
    assert not sequence.on_change.is_observed()
    assert not sequence.delta_observable.is_observed()

    sequence.on_change.observe(lambda _: None)
    assert not sequence.on_change.is_observed()

    sequence.delta_observable.observe(lambda _: None)
    assert not sequence.delta_observable.is_observed()


def test_static_sequence_str():
    sequence = StaticObservableSequence([1, 2, 3])
    assert str(sequence) == "[1, 2, 3]"


def test_static_sequence_length():
    sequence = StaticObservableSequence([1, 2, 3])
    assert len(sequence) == 3
    assert sequence.length_value.value == 3
    assert sequence.length_value.constant_value_or_raise == 3


def test_static_sequence_get_item():
    sequence = StaticObservableSequence([1, 2, 3])
    assert sequence[0] == 1
    assert sequence[1] == 2
    assert sequence[2] == 3


def test_static_sequence_iter():
    sequence = StaticObservableSequence([1, 2, 3])
    assert list(sequence) == [1, 2, 3]


def test_static_sequence_contains():
    sequence = StaticObservableSequence([1, 2, 3])
    assert 1 in sequence
    assert 2 in sequence
    assert 3 in sequence
    assert 4 not in sequence
    assert "test" not in sequence


def test_static_sequence_has_no_append():
    sequence = StaticObservableSequence([1, 2, 3])
    with pytest.raises(AttributeError):
        sequence.append(4)


def test_static_sequence_has_no_remove():
    sequence = StaticObservableSequence([1, 2, 3])
    with pytest.raises(AttributeError):
        sequence.remove(2)


def test_static_sequence_equals_true():
    seq1 = StaticObservableSequence([1, 2, 3])
    seq2 = StaticObservableSequence([1, 2, 3])
    assert seq1 == seq2


def test_static_sequence_equals_false():
    seq1 = StaticObservableSequence([1, 2, 3])
    seq2 = StaticObservableSequence([1, 2, 4])
    assert seq1 != seq2


def test_static_sequence_equals_observable_list_true():
    seq1 = StaticObservableSequence([1, 2, 3])
    seq2 = ObservableList([1, 2, 3])
    assert seq1 == seq2


def test_static_sequence_equals_observable_list_false():
    seq1 = StaticObservableSequence([1, 2, 3])
    seq2 = ObservableList([1, 2, 4])
    assert seq1 != seq2


def test_frozen_sequence_hash_equal():
    seq1 = FrozenObservableSequence([1, 2, 3])
    seq2 = FrozenObservableSequence([1, 2, 3])
    assert hash(seq1) == hash(seq2)


def test_frozen_sequence_hash_not_equal():
    seq1 = FrozenObservableSequence([1, 2, 3])
    seq2 = FrozenObservableSequence([1, 2, 4])
    assert hash(seq1) != hash(seq2)
