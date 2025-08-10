from typing import Any, Callable, Iterator

from fastcrawl.core import type_validation


class Component:
    """Wrapper for components like handlers or pipelines.

    Args:
        func (Callable): The function to be wrapped.
        expected_arg (type_validation.FuncArg): The expected type of the function's main argument for validation.
        expected_return_type (type_validation.FuncReturnType): The expected return type of the function for validation.

    """

    _func: Callable
    _validator: type_validation.FuncTypeValidator

    def __init__(
        self,
        func: Callable,
        expected_arg: type_validation.FuncArg,
        expected_return_type: type_validation.FuncReturnType,
    ) -> None:
        self._func = func
        self._validator = type_validation.FuncTypeValidator(func, expected_arg, expected_return_type)

    def is_value_match_to_arg(self, value: Any) -> bool:
        """Returns True if the value matches the main argument type, False otherwise."""
        return self._validator.is_value_match_to_arg(value)

    def run_iter(self, **kwargs) -> Iterator[Any]:
        """Yields the result of the function call, validating its return type."""
        result = self._func(**kwargs)
        yield from self._validator.validate_return_value(result)

    def run(self, **kwargs) -> Any:
        """Returns the result of the function call, validating its return type."""
        return next(self.run_iter(**kwargs))
