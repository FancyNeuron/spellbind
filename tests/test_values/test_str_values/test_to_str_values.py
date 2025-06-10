from spellbind.values import SimpleVariable


def test_to_str_of_int_42():
    value = SimpleVariable(42)
    to_str_value = value.to_str()

    assert to_str_value.value == "42"

    value.value = 100

    assert to_str_value.value == "100"
