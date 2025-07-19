from typing import override


class Base:
    def some_method(self) -> str:
        return "This is a method from the Base class."


class Sub(Base):
    def some_method(self) -> str:
        return "This is a method from the Sub class."

    @override
    def some_methods(self) -> str:
        return "This is a method from the Sub class."
