from spellbind.bool_values import BoolConstant, BoolVariable


def test_bool_constant_true_to_str():
    const = BoolConstant(True)
    assert str(const) == "True"


def test_bool_constant_false_to_str():
    const_false = BoolConstant(False)
    assert str(const_false) == "False"


def test_logical_not_variable_true():
    var = BoolVariable(True)
    negated = var.logical_not()
    assert not negated.value


def test_logical_not_variable_false():
    var = BoolVariable(False)
    negated = var.logical_not()
    assert negated.value


def test_logical_not_flip_flop():
    var = BoolVariable(True)
    negated = var.logical_not()
    assert not negated.value

    var.value = False
    assert negated.value

    var.value = True
    assert not negated.value


def test_logical_not_double_negation():
    var = BoolVariable(True)
    double_negated = var.logical_not().logical_not()
    assert double_negated.value

    var.value = False
    assert not double_negated.value
