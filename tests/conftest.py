from typing import Iterable, Any, overload, Collection
from unittest.mock import Mock

from spellbind.actions import SequenceDeltaAction
from spellbind.collections import ObservableSequence


class Call:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.args == other.args and self.kwargs == other.kwargs
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


class SequenceObservers(Observers):
    def __init__(self, observable_sequence: ObservableSequence):
        self.on_change_observer = OneParameterObserver()
        self.delta_observer = OneParameterObserver()
        observable_sequence.on_change.observe(self.on_change_observer)
        observable_sequence.delta_observable.observe_single(self.delta_observer)
        super().__init__(self.on_change_observer, self.delta_observer)

    def assert_added_calls(self, *expected_adds: tuple[int, Any]):
        self.assert_calls(*((index, value, True) for index, value in expected_adds))

    def assert_removed_calls(self, *expected_removes: tuple[int, Any]):
        self.assert_calls(*((index, value, False) for index, value in expected_removes))

    def assert_calls(self, *expected_calls: tuple[int, Any, bool]):
        delta_calls = self.delta_observer.calls
        assert len(delta_calls) == len(expected_calls), f"Expected {len(expected_calls)} calls, got {len(delta_calls)}"
        for i, (call, expected_call) in enumerate(zip(delta_calls, expected_calls)):
            expected_index, expected_value, expected_added = expected_call
            action: SequenceDeltaAction = call.get_arg()
            assert action.is_add == expected_added, f"Error parameter {i}. Expected {'add' if expected_added else 'remove'}, got {'add' if action.is_add else 'remove'}"
            assert action.index == expected_index, f"Error parameter {i}. Expected index {expected_index}, got {action.index}"
            assert action.value == expected_value, f"Error parameter {i}. Expected value {expected_value}, got {action.value}"
