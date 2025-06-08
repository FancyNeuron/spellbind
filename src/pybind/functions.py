import inspect
from inspect import Parameter
from typing import Callable


def _is_positional_parameter(param: Parameter) -> bool:
    return param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)


def count_positional_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for parameter in parameters.values() if _is_positional_parameter(parameter))


def _is_required_positional_parameter(param: Parameter) -> bool:
    return param.default == param.empty and _is_positional_parameter(param)


def count_non_default_parameters(function: Callable) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for param in parameters.values() if _is_required_positional_parameter(param))


def assert_parameter_max_count(callable_: Callable, max_count: int) -> None:
    if count_non_default_parameters(callable_) > max_count:
        if hasattr(callable_, '__name__'):
            callable_name = callable_.__name__
        elif hasattr(callable_, '__class__'):
            callable_name = callable_.__class__.__name__
        else:
            callable_name = str(callable_)
        raise ValueError(f"Callable {callable_name} has too many non-default parameters: "
                         f"{count_non_default_parameters(callable_)} > {max_count}")
