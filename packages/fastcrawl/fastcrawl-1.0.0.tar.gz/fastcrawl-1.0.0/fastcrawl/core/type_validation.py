import collections.abc
import dataclasses
import inspect
import sys
import types
from typing import Any, Callable, Dict, Iterator, Optional, Tuple, Type, Union, get_type_hints


@dataclasses.dataclass(frozen=True)
class FuncArg:
    """Represents the expected type of a function's main argument.

    Attributes:
        name (str): The name of the argument.
        types (Tuple[Type, ...]): A tuple of expected types for the argument.

    """

    name: str
    types: Tuple[Type, ...]


@dataclasses.dataclass(frozen=True)
class FuncReturnType:
    """Represents the expected return type of a function.

    Attributes:
        is_iterator (bool): Indicates if the return type can be an iterator.
        types (Tuple[Type, ...]): A tuple of expected types for the return value.

    """

    is_iterator: bool
    types: Tuple[Type, ...]


class FuncTypeValidator:
    """Validator for function types.

    Args:
        func (Callable): The function to validate.
        expected_arg (FuncArg): The expected type of the function's main argument.
        expected_return_type (FuncReturnType): The expected return type of the function.

    """

    _func_name: str
    _type_hints: Dict[str, Any]
    _arg: FuncArg
    _return_type: FuncReturnType

    def __init__(self, func: Callable, expected_arg: FuncArg, expected_return_type: FuncReturnType) -> None:
        self._func_name = func.__name__
        self._type_hints = get_type_hints(func)
        self._arg = self._validate_arg(expected_arg)
        self._return_type = self._validate_return_type(expected_return_type)

    def is_value_match_to_arg(self, value: Any) -> bool:
        """Returns True if the value matches the main argument type, False otherwise."""
        return isinstance(value, self._arg.types)

    def validate_return_value(self, value: Any) -> Iterator[Any]:
        """Validates the return value of the function against the expected return type.

        Args:
            value (Any): The value to validate.

        Yields:
            Any: The validated value if it matches the expected return type.

        Raises:
            ValueError: If the value does not match the expected return type.

        """
        if self._return_type.is_iterator:
            if not hasattr(value, "__iter__"):
                raise ValueError(
                    f"Function `{self._func_name}` returned a non-iterable value {value}, "
                    f"expected an iterable of {self._return_type.types}."
                )
            for item in value:
                if not isinstance(item, self._return_type.types):
                    raise ValueError(
                        f"Function `{self._func_name}` returned an invalid item {type(item)}, "
                        f"expected iterator of {self._return_type.types}."
                    )
                yield item
        else:
            if not isinstance(value, self._return_type.types):
                raise ValueError(
                    f"Function `{self._func_name}` returned an invalid item {type(value)}, "
                    f"expected one of {self._return_type.types}."
                )
            yield value

    def _validate_arg(self, expected: FuncArg) -> FuncArg:
        actual_type = self._type_hints.get(expected.name)

        if actual_type and self._is_valid_type(actual_type, expected.types):
            return FuncArg(name=expected.name, types=(actual_type,))

        raise TypeError(
            f"Function `{self._func_name}` must have a `{expected.name}` argument "
            f"with one of the following types: {expected.types}"
        )

    def _validate_return_type(self, expected: FuncReturnType) -> FuncReturnType:
        actual_type = self._type_hints.get("return")
        if actual_type is None:
            actual_type = type(None)
        validated_type = self._is_valid_return_type(actual_type, expected)

        if not validated_type:
            error_message = (
                f"Function `{self._func_name}` has an invalid return type hint. "
                f"Expected one of the following or a union of them"
            )
            if expected.is_iterator:
                error_message += " or an `Iterator` of them"
            error_message += f": {expected.types}"
            raise TypeError(error_message)

        return validated_type

    def _is_valid_return_type(self, actual: Any, expected: FuncReturnType) -> Optional[FuncReturnType]:
        if self._is_valid_type(actual, expected.types):
            return FuncReturnType(is_iterator=False, types=(actual,))

        actual_type_origin = getattr(actual, "__origin__", actual)

        if self._is_type_is_union(actual_type_origin) and all(
            self._is_valid_type(arg, expected.types) for arg in actual.__args__
        ):
            return FuncReturnType(is_iterator=False, types=actual.__args__)

        if expected.is_iterator and actual_type_origin is collections.abc.Iterator and len(actual.__args__) == 1:
            validated_child_type = self._is_valid_return_type(
                actual=actual.__args__[0],
                expected=FuncReturnType(is_iterator=False, types=expected.types),
            )
            if validated_child_type:
                return FuncReturnType(
                    is_iterator=True,
                    types=validated_child_type.types,
                )

        return None

    def _is_valid_type(self, actual: Any, expected: Tuple[Type, ...]) -> bool:
        return inspect.isclass(actual) and issubclass(actual, expected)

    def _is_type_is_union(self, actual: Any) -> bool:
        if actual is Union:
            return True
        if sys.version_info >= (3, 10):
            return isinstance(actual, types.UnionType)
        return False
