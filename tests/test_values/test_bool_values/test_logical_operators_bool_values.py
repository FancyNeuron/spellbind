from spellbind.bool_values import BoolVariable


def test_bool_variables_and_variable_true_variable_true():
    var1 = BoolVariable(True)
    var2 = BoolVariable(True)
    result = var1 & var2
    assert result.value

    var1.value = False
    assert not result.value


def test_bool_variables_and_variable_true_variable_false():
    var1 = BoolVariable(True)
    var2 = BoolVariable(False)
    result = var1 & var2
    assert not result.value

    var2.value = True
    assert result.value


def test_bool_variables_and_variable_false_variable_false():
    var1 = BoolVariable(False)
    var2 = BoolVariable(False)
    result = var1 & var2
    assert not result.value

    var1.value = True
    assert not result.value


def test_bool_variable_and_variable_true_literal_false():
    var = BoolVariable(True)
    result = var & False
    assert not result.value

    var.value = False
    assert not result.value


def test_bool_variable_and_literal_false_variable_true():
    var = BoolVariable(True)
    result = False & var
    assert not result.value

    var.value = False
    assert not result.value


def test_bool_variables_or_variable_true_variable_true():
    var1 = BoolVariable(True)
    var2 = BoolVariable(True)
    result = var1 | var2
    assert result.value

    var1.value = False
    assert result.value


def test_bool_variables_or_variable_true_variable_false():
    var1 = BoolVariable(True)
    var2 = BoolVariable(False)
    result = var1 | var2
    assert result.value

    var1.value = False
    assert not result.value


def test_bool_variables_or_variable_false_variable_false():
    var1 = BoolVariable(False)
    var2 = BoolVariable(False)
    result = var1 | var2
    assert not result.value

    var2.value = True
    assert result.value


def test_bool_variable_or_variable_false_literal_true():
    var = BoolVariable(False)
    result = var | True
    assert result.value

    var.value = True
    assert result.value


def test_bool_variable_or_literal_true_variable_false():
    var = BoolVariable(False)
    result = True | var
    assert result.value

    var.value = True
    assert result.value


def test_bool_variables_xor_variable_true_variable_true():
    var1 = BoolVariable(True)
    var2 = BoolVariable(True)
    result = var1 ^ var2
    assert not result.value

    var1.value = False
    assert result.value


def test_bool_variables_xor_variable_true_variable_false():
    var1 = BoolVariable(True)
    var2 = BoolVariable(False)
    result = var1 ^ var2
    assert result.value

    var2.value = True
    assert not result.value


def test_bool_variables_xor_variable_false_variable_false():
    var1 = BoolVariable(False)
    var2 = BoolVariable(False)
    result = var1 ^ var2
    assert not result.value

    var1.value = True
    assert result.value


def test_bool_variable_xor_variable_true_literal_true():
    var = BoolVariable(True)
    result = var ^ True
    assert not result.value

    var.value = False
    assert result.value


def test_bool_variable_xor_literal_true_variable_true():
    var = BoolVariable(True)
    result = True ^ var
    assert not result.value

    var.value = False
    assert result.value
