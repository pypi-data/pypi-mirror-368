from types import UnionType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from wexample_helpers.exception.not_allowed_variable_type_exception import NotAllowedVariableTypeException


def type_is_generic(type_value: Any) -> bool:
    """Detects if a given type is a generic type like List, Dict, Union"""

    # Set of known generic types for quick membership testing
    generic_types = {list, dict, tuple, List, Dict, Tuple, Union}

    # Extract the base type of type_value using get_origin, or use type_value itself if get_origin is None
    type_value = get_origin(type_value) or type_value

    # Check if type_value is a known generic type
    return type_value in generic_types


def type_validate_or_fail(value: Any, allowed_type: Type | UnionType) -> None:
    if allowed_type is Any:
        return

    if allowed_type is Callable:
        if callable(value):
            return
        # Not a callable where one was expected
        raise NotAllowedVariableTypeException(
            variable_type=type(value).__name__,
            variable_value=value,
            allowed_types=["callable"],
        )

    # Check if the raw value matches any allowed base type
    if not type_is_generic(allowed_type):
        if isinstance(allowed_type, Callable):
            if isinstance(value, Callable):
                # Type is probably not a meta type, i.e:
                #   - allowed_type=Type[MyClass] will match value MyClass
                #   - allowed_type=MyClass will not match value MyClass
                if isinstance(allowed_type, type):
                    raise NotAllowedVariableTypeException(
                        variable_type=type(value).__name__,
                        variable_value=value,
                        allowed_types=[allowed_type],
                    )

                args = get_args(allowed_type)
                if args:
                    return_type = args[-1]

                    try:
                        type_hints = get_type_hints(value, localns=locals())
                        actual_return_type_hint = type_hints.get("return", None)
                    except NameError:
                        actual_return_type_hint = None

                    if actual_return_type_hint is None:
                        return

                    # Handle generic types
                    if type_is_compatible(
                        actual_type=cast(Type, actual_return_type_hint),
                        allowed_type=return_type,
                    ):
                        return

                    raise NotAllowedVariableTypeException(
                        variable_type=str(actual_return_type_hint),
                        variable_value=value,
                        allowed_types=[return_type],
                    )

                return
        # Explicit check for simple types without get_origin
        elif isinstance(value, allowed_type):
            return

    # Handle generic types
    if type_generic_value_is_valid(value, allowed_type):
        return

    # If none of the checks passed, raise an exception
    raise NotAllowedVariableTypeException(
        variable_type=type(value).__name__,
        variable_value=value,
        allowed_types=[allowed_type]
    )


def type_generic_value_is_valid(value: Any, allowed_type: Type | UnionType) -> bool:
    """Helper to recursively validate parameter types for generics like Dict, List, Set, Tuple, and Union."""
    origin = get_origin(allowed_type) or allowed_type
    args = get_args(allowed_type)

    # Validate Union type by checking if value matches any of the types in the Union
    if origin is Union:
        return any(type_generic_value_is_valid(value, arg) for arg in args)

    # Validate dictionary type with possible nested generics
    if origin is dict:
        if not isinstance(value, dict):
            return False
        # Accept empty dict
        if not value:
            return True
        # Validate key and value types recursively
        key_type, value_type = args if len(args) == 2 else (Any, Any)
        return all(
            type_generic_value_is_valid(k, key_type)
            and type_generic_value_is_valid(v, value_type)
            for k, v in value.items()
        )

    # Validate list type with possible nested generics
    elif origin is list:
        if not isinstance(value, list):
            return False
        # Accept empty list
        if not value:
            return True
        # Validate item type recursively
        item_type = args[0] if args else Any
        return all(type_generic_value_is_valid(item, item_type) for item in value)

    # Validate set type with possible nested generics
    elif origin is set:
        if not isinstance(value, set):
            return False
        # Accept empty set
        if not value:
            return True
        # Validate item type recursively
        item_type = args[0] if args else Any
        return all(type_generic_value_is_valid(item, item_type) for item in value)

    # Validate tuple type with possible nested generics
    elif origin is tuple:
        if not isinstance(value, tuple) or (args and len(value) != len(args)):
            return False
        # Validate each item in the tuple recursively
        return all(
            type_generic_value_is_valid(item, arg)
            for item, arg in zip(value, args)
            if args
        )

    elif origin is Any:
        return True

    # For any other types, fallback to isinstance check
    return isinstance(value, origin)



def type_is_compatible(actual_type: Type, allowed_type: Type) -> bool:
    """Check if actual_type is compatible with allowed_type for generics like Dict, List, Tuple, and Union."""
    origin = get_origin(allowed_type) or allowed_type
    actual_origin = get_origin(actual_type) or actual_type
    allowed_args = get_args(allowed_type)
    actual_args = get_args(actual_type)

    # If allowed_type is Any, it is compatible with any actual_type
    if origin is Any:
        return True

    # Handle Union type for allowed_type
    if origin is Union:
        return any(type_is_compatible(actual_type, arg) for arg in allowed_args)

    # Handle Callable type with possible nested generics
    if issubclass(origin, Callable):
        # Check if actual_type is also a Callable
        if not issubclass(actual_origin, Callable):
            return False
        # If allowed_type is just Callable without specific args, consider it compatible with any Callable
        if not allowed_args:
            return True
        # If allowed_type has specific args, compare return types (last element in allowed_args)
        if len(allowed_args) == len(actual_args):
            return type_is_compatible(actual_args[-1], allowed_args[-1])
        return False

    # Handle dictionary type with possible nested generics
    if origin is dict:
        if actual_origin is not dict:
            return False
        # Check compatibility for key and value types recursively
        key_type, value_type = allowed_args if len(allowed_args) == 2 else (Any, Any)
        actual_key_type, actual_value_type = (
            actual_args if len(actual_args) == 2 else (Any, Any)
        )
        return type_is_compatible(actual_key_type, key_type) and type_is_compatible(
            actual_value_type, value_type
        )

    # Handle list type with possible nested generics
    elif origin is list:
        if actual_origin is not list:
            return False
        # Validate item type recursively
        item_type = allowed_args[0] if allowed_args else Any
        actual_item_type = actual_args[0] if actual_args else Any
        return type_is_compatible(actual_item_type, item_type)

    # Handle tuple type with possible nested generics
    elif origin is tuple:
        if actual_origin is not tuple or len(actual_args) != len(allowed_args):
            return False
        # Validate each item type in the tuple recursively
        return all(
            type_is_compatible(act, exp) for act, exp in zip(actual_args, allowed_args)
        )

    # For other types, fall back to direct comparison
    return actual_type == allowed_type

def type_to_name(t: Any) -> str:
    # Accept python types, strings, and mypy UnionType
    if isinstance(t, str):
        return t
    if isinstance(t, type):
        return t.__name__
    if isinstance(t, UnionType):
        # Convert "A | B" style if possible
        try:
            return " | ".join(type_to_name(it) for it in t.items)
        except Exception:
            return str(t)
    return str(t)