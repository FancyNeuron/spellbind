import inspect
from inspect import Parameter
from typing import Callable, Any


def is_positional_parameter(param: Parameter) -> bool:
    return param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)


def has_var_args(function: Callable[..., Any]) -> bool:
    parameters = inspect.signature(function).parameters
    return any(param.kind == Parameter.VAR_POSITIONAL for param in parameters.values())


def count_positional_parameters(function: Callable[..., Any]) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for parameter in parameters.values() if is_positional_parameter(parameter))


def is_required_positional_parameter(param: Parameter) -> bool:
    return param.default == param.empty and is_positional_parameter(param)


def count_non_default_parameters(function: Callable[..., Any]) -> int:
    parameters = inspect.signature(function).parameters
    return sum(1 for param in parameters.values() if is_required_positional_parameter(param))


def assert_parameter_max_count(callable_: Callable[..., Any], max_count: int) -> None:
    if count_non_default_parameters(callable_) > max_count:
        if hasattr(callable_, '__name__'):
            callable_name = callable_.__name__
        elif hasattr(callable_, '__class__'):
            callable_name = callable_.__class__.__name__
        else:
            callable_name = str(callable_)  # pragma: no cover
        raise ValueError(f"Callable {callable_name} has too many non-default parameters: "
                         f"{count_non_default_parameters(callable_)} > {max_count}")
