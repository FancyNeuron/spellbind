import ast
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Sequence, Callable, Generator, Tuple
from typing import Iterable, overload, Collection
from unittest.mock import Mock

import pytest
from typing_extensions import TypeVar

from spellbind.actions import AtIndexDeltaAction, CollectionAction, DeltaAction
from spellbind.observable_collections import ObservableCollection
from spellbind.observable_sequences import ObservableSequence, ValueSequence

_S = TypeVar("_S")


PROJECT_ROOT_PATH = Path(__file__).parent.parent.resolve()
SOURCE_PATH = PROJECT_ROOT_PATH / "src"


def iter_python_files(source_path: Path) -> Generator[Path, None, None]:
    yield from source_path.rglob("*.py")


def is_class_definition(module_path: Path, object_name: str) -> bool:
    text = module_path.read_text(encoding="utf-8")
    node = ast.parse(text, filename=str(module_path))
    for item in node.body:
        if hasattr(item, "name") and getattr(item, "name") == object_name:
            if isinstance(item, ast.ClassDef):
                return True
            else:
                return False
    return False


def resolve_module_path(base_path: Path, module: str) -> Path:
    unfinished_module_path = base_path / Path(*module.split("."))
    init_path = unfinished_module_path / "__init__.py"
    if init_path.exists():
        return init_path
    file_path = unfinished_module_path.with_suffix(".py")
    return file_path


def is_class_import(alias: ast.alias, import_: ast.ImportFrom, source_root: Path = SOURCE_PATH) -> bool:
    module = import_.module
    if module is None:
        return False
    module_path = resolve_module_path(source_root, module)
    if module_path is None:
        return False
    return is_class_definition(module_path, alias.name)


def iter_imported_aliases(file_path: Path) -> Generator[Tuple[ast.alias, ast.ImportFrom], None, None]:
    text = file_path.read_text(encoding="utf-8")
    node = ast.parse(text, filename=str(file_path))
    for statement in ast.walk(node):
        if isinstance(statement, ast.ImportFrom):
            for alias_ in statement.names:
                yield alias_, statement


class Call:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.args == other.args and self.kwargs == other.kwargs
        if len(self.kwargs) == 0 and len(self.args) == 1:
            return self.args[0] == other
        elif isinstance(other, (int, float, str, bool)):
            if len(self.kwargs) > 0:
                return False
            if len(self.args) != 1:
                return False
            return self.args[0] == other
        elif isinstance(other, Collection):
            if len(self.kwargs) > 0:
                return False
            return self.args == other

        return False

    def __repr__(self):
        args_repr = ", ".join(repr(arg) for arg in self.args)
        kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
        return f"Call({args_repr}, {kwargs_repr})" if kwargs_repr else f"Call({args_repr})"

    def get_arg(self) -> Any:
        assert len(self.args) == 1
        assert len(self.kwargs) == 0
        return self.args[0]


class Observer(Mock):
    calls: list[Call]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.calls.append(Call(*args, **kwargs))


class NoParametersObserver(Observer):
    def __call__(self):
        super().__call__()


class OneParameterObserver(Observer):
    def __call__(self, param0):
        super().__call__(param0)


class OneDefaultParameterObserver(Observer):
    def __call__(self, param0="default"):
        super().__call__(param0)


class TwoParametersObserver(Observer):
    def __call__(self, param0, param1):
        super().__call__(param0, param1)


class OneRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1="default"):
        super().__call__(param0, param1)


class TwoDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1"):
        super().__call__(param0, param1)


class ThreeParametersObserver(Observer):
    def __call__(self, param0, param1, param2):
        super().__call__(param0, param1, param2)


class ThreeDefaultParametersObserver(Observer):
    def __call__(self, param0="default0", param1="default1", param2="default2"):
        super().__call__(param0=param0, param1=param1, param2=param2)


class TwoRequiredOneDefaultParameterObserver(Observer):
    def __call__(self, param0, param1, param2="default2"):
        super().__call__(param0, param1, param2)


class Observers:
    def __init__(self, *observers: Observer):
        self._observers = tuple(observers)

    def __iter__(self):
        return iter(self._observers)

    def assert_not_called(self):
        for observer in self:
            observer.assert_not_called()


class SequencePairObservers(Observers):
    def __init__(self, observer: OneParameterObserver, index_observer: TwoParametersObserver):
        self.observer = observer
        self.index_observer = index_observer
        super().__init__(self.observer, self.index_observer)

    @overload
    def assert_called(self, indices_with_values: Iterable[tuple[int, Any]]): ...

    @overload
    def assert_called(self, index: int, value: Any): ...

    def assert_called(self, index, value=None):
        if isinstance(index, int):
            self.observer.assert_called_once_with((value,))
            self.index_observer.assert_called_once_with((value, index))
        else:
            assert self.observer.calls == tuple(value for _, value in index)
            assert self.index_observer.calls == tuple((value, index) for index, value in index)


def append_bool(v: Any | tuple[int, Any], b: bool) -> tuple:
    if isinstance(v, tuple):
        return tuple([*v, b])
    else:
        return v, b


class ValueSequenceObservers(Observers):
    def __init__(self, value_sequence: ObservableSequence):
        self.on_change_observer = OneParameterObserver()
        self.delta_observer = OneParameterObserver()
        if isinstance(value_sequence, ValueSequence):
            value_sequence.on_value_change.observe(self.on_change_observer)
            value_sequence.value_delta_observable.observe_single(self.delta_observer)
        else:
            value_sequence.on_change.observe(self.on_change_observer)
            value_sequence.delta_observable.observe_single(self.delta_observer)
        super().__init__(self.on_change_observer, self.delta_observer)

    def assert_added_calls(self, *expected_adds: Any | tuple[int, Any]):
        self.assert_calls(*(append_bool(add, True) for add in expected_adds))

    def assert_removed_calls(self, *expected_removes: Any | tuple[int, Any]):
        self.assert_calls(*(append_bool(remove, False) for remove in expected_removes))

    def assert_calls(self, *expected_calls: tuple[Any, bool] | tuple[int, Any, bool]):
        delta_calls = self.delta_observer.calls
        if not len(delta_calls) == len(expected_calls):
            pytest.fail(f"Expected {len(expected_calls)} calls, got {len(delta_calls)}")
        for i, (call, expected_call) in enumerate(zip(delta_calls, expected_calls)):
            action = call.get_arg()
            assert isinstance(action, DeltaAction)
            if len(expected_call) == 2:
                expected_value, expected_added = expected_call
                assert not isinstance(action, AtIndexDeltaAction)
            elif len(expected_call) == 3:
                expected_index, expected_value, expected_added = expected_call
                assert isinstance(action, AtIndexDeltaAction)
                if not action.index == expected_index:
                    pytest.fail(f"Error call {i}. Expected index {expected_index}, got {action.index}")
            else:
                raise ValueError
            if not action.is_add == expected_added:
                pytest.fail(f"Error call {i}. Expected {'add' if expected_added else 'remove'}, got {'add' if action.is_add else 'remove'}")
            if not action.value == expected_value:
                pytest.fail(f"Error call {i}. Expected value {expected_value}, got {action.value}")

    def assert_actions(self, *actions: CollectionAction):
        assert self.on_change_observer.calls == [*actions]

    def assert_single_action(self, action: CollectionAction):
        self.on_change_observer.assert_called_once_with(action)


class ValueCollectionObservers(Observers):
    def __init__(self, collection: ObservableCollection):
        self.on_change_observer = OneParameterObserver()
        self.delta_observer = OneParameterObserver()
        collection.on_change.observe(self.on_change_observer)
        collection.delta_observable.observe_single(self.delta_observer)
        super().__init__(self.on_change_observer, self.delta_observer)

    def assert_added_calls(self, *expected_adds: Any):
        self.assert_calls(*(append_bool(add, True) for add in expected_adds))

    def assert_removed_calls(self, *expected_removes: Any):
        self.assert_calls(*(append_bool(remove, False) for remove in expected_removes))

    def assert_calls(self, *expected_calls: tuple[Any, bool]):
        delta_calls = self.delta_observer.calls
        if not len(delta_calls) == len(expected_calls):
            pytest.fail(f"Expected {len(expected_calls)} calls, got {len(delta_calls)}")
        for i, (call, expected_call) in enumerate(zip(delta_calls, expected_calls)):
            action = call.get_arg()
            assert isinstance(action, DeltaAction)
            expected_value, expected_added = expected_call
            if not action.is_add == expected_added:
                pytest.fail(f"Error call {i}. Expected {'add' if expected_added else 'remove'}, got {'add' if action.is_add else 'remove'}")
            if not action.value == expected_value:
                pytest.fail(f"Error call {i}. Expected value {expected_value}, got {action.value}")

    def assert_actions(self, *actions: CollectionAction):
        assert self.on_change_observer.calls == [*actions]

    def assert_single_action(self, action: CollectionAction):
        assert len(self.on_change_observer.calls) == 1
        assert self.on_change_observer.calls[0] == action


@contextmanager
def assert_length_changed_during_action_events_but_notifies_after(collection: ObservableCollection, expected_length: int):
    events = []

    def assert_list_length():
        events.append("changed")
        assert len(collection) == expected_length
        assert collection.length_value.value == expected_length

    collection.delta_observable.observe(assert_list_length)
    collection.length_value.observe(lambda i: events.append(f"length set to {expected_length}"))
    yield
    assert events == ["changed", f"length set to {expected_length}"]


def values_factories() -> Sequence[Callable[[_S, ...], Iterable[_S]]]:
    return [
        lambda *values: tuple(values),
        lambda *values: list(values),
        lambda *values: (value for value in values),
    ]


def void_observer(*args, **kwargs):
    pass
