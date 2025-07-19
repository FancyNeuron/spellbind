import pytest

from conftest import OneParameterObserver
from spellbind.event import ValuesEvent
from spellbind.observables import ValuesObservable


@pytest.mark.parametrize("weakly", [True, False])
def test_derive_values_event(weakly: bool):
    event = ValuesEvent[str]()
    derived: ValuesObservable[int] = event.map(lambda x: len(x), weakly=weakly)
    observer = OneParameterObserver()
    derived.observe(observer)

    event(("apple", "banana", "fig"))

    observer.assert_called_once_with((5, 6, 3))


@pytest.mark.parametrize("weakly", [True, False])
def test_derive_values_is_lazy(weakly: bool):
    derived_parameters = []

    def derive_str(value: str) -> int:
        derived_parameters.append(value)
        return len(value)

    event = ValuesEvent[str]()
    derived: ValuesObservable[int] = event.map(derive_str, weakly=weakly)
    event(("apple", "banana", "fig"))
    assert derived_parameters == []
