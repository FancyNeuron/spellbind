from conftest import OneParameterObserver
from spellbind.str_collections import ObservableStrList


def test_reduce_str_list():
    str_list = ObservableStrList(["foo", "bar"])

    def remove_reducer(acc: str, to_remove: str) -> str:
        result = acc
        for s in to_remove:
            result = result.replace(s, "")
        return result

    concatenated = str_list.reduce_to_str(lambda acc, s: "".join(sorted(acc + s)), remove_reducer, "")
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "abfoor"
    str_list.append("baz")
    assert concatenated.value == "aabbfoorz"
    del str_list[0]
    assert concatenated.value == "aabbrz"


def test_sum_int_list_append_sequentially():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.append("lorem")
    assert concatenated.value == "foobarbazlorem"
    str_list.append("ipsum")
    assert concatenated.value == "foobarbazloremipsum"
    str_list.append("dolor")
    assert concatenated.value == "foobarbazloremipsumdolor"
    assert observer.calls == ["foobarbazlorem", "foobarbazloremipsum", "foobarbazloremipsumdolor"]


def test_sum_int_list_clear():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.clear()
    assert concatenated.value == ""
    observer.assert_called_once_with("")


def test_sum_int_list_del_sequentially():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    del str_list[0]
    assert concatenated.value == "barbaz"
    del str_list[0]
    assert concatenated.value == "baz"
    del str_list[0]
    assert concatenated.value == ""
    assert observer.calls == ["barbaz", "baz", ""]


def test_sum_int_list_del_slice():
    str_list = ObservableStrList(["foo", "bar", "baz", "lorem", "ipsum"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbazloremipsum"
    del str_list[1:4]
    assert concatenated.value == "fooipsum"
    assert observer.calls == ["fooipsum"]


def test_sum_int_list_extend():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.extend(["lorem", "ipsum"])
    assert concatenated.value == "foobarbazloremipsum"
    str_list.extend(["dolor"])
    assert concatenated.value == "foobarbazloremipsumdolor"
    assert observer.calls == ["foobarbazloremipsum", "foobarbazloremipsumdolor"]


def test_sum_int_list_insert():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.insert(0, "lorem")
    assert concatenated.value == "loremfoobarbaz"
    str_list.insert(2, "ipsum")
    assert concatenated.value == "loremfooipsumbarbaz"
    str_list.insert(5, "dolor")
    assert concatenated.value == "loremfooipsumbarbazdolor"
    assert observer.calls == ["loremfoobarbaz", "loremfooipsumbarbaz", "loremfooipsumbarbazdolor"]


def test_sum_int_list_insert_all():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.insert_all(((1, "lorem"), (2, "ipsum"), (3, "dolor")))
    assert concatenated.value == "foolorembaripsumbazdolor"
    assert observer.calls == ["foolorembaripsumbazdolor"]


def test_sum_int_list_setitem():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list[0] = "lorem"
    assert concatenated.value == "lorembarbaz"
    str_list[1] = "ipsum"
    assert concatenated.value == "loremipsumbaz"
    str_list[2] = "dolor"
    assert concatenated.value == "loremipsumdolor"
    assert observer.calls == ["lorembarbaz", "loremipsumbaz", "loremipsumdolor"]


def test_sum_int_list_set_slice():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list[0:3] = ["lorem", "ipsum", "dolor"]
    assert concatenated.value == "loremipsumdolor"
    assert observer.calls == ["loremipsumdolor"]


def test_sum_int_list_reverse():
    str_list = ObservableStrList(["foo", "bar", "baz"])
    concatenated = str_list.concatenated
    observer = OneParameterObserver()
    concatenated.observe(observer)
    assert concatenated.value == "foobarbaz"
    str_list.reverse()
    assert concatenated.value == "bazbarfoo"
    assert observer.calls == ["bazbarfoo"]
