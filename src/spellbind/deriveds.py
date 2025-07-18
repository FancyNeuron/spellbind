from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class Derived(ABC):
    @property
    @abstractmethod
    def derived_from(self) -> frozenset[Derived]: ...

    @property
    def deep_derived_from(self) -> Iterable[Derived]:
        found_derived = set()
        derive_queue = [self]

        while derive_queue:
            current = derive_queue.pop(0)
            for dependency in current.derived_from:
                if dependency not in found_derived:
                    found_derived.add(dependency)
                    yield dependency
                    derive_queue.append(dependency)

    def is_derived_from(self, derived: Derived) -> bool:
        for dependency in self.deep_derived_from:
            if derived is dependency:
                return True
        return False
