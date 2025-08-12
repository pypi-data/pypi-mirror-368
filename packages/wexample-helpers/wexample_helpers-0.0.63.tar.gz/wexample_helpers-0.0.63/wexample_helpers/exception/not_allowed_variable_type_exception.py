from typing import List, Optional, Any

from wexample_helpers.exception.not_allowed_item_exception import NotAllowedItemException


class NotAllowedVariableTypeException(NotAllowedItemException):
    """A specific exception for bad variables types"""
    error_code: str = "NOT_ALLOWED_VARIABLE_TYPE"

    def __init__(
            self,
            variable_type: Any,
            variable_value: Any,
            allowed_types: Optional[List[Any]] = None,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None
    ):
        from wexample_helpers.helpers.string import string_truncate
        from wexample_helpers.helpers.type import type_to_name

        # Normalize variable_type for display
        var_type_name = type_to_name(variable_type)

        # Normalize allowed types for message and payload
        allowed_types = allowed_types or []
        allowed_type_names = [type_to_name(t) for t in allowed_types]
        types_str = ", ".join(allowed_type_names) if allowed_type_names else "<none>"

        super().__init__(
            item_type='type',
            item_value=var_type_name,
            allowed_values=allowed_type_names,
            cause=cause,
            previous=previous,
            message=(
                f"Invalid variable type '{var_type_name}' for value "
                f"{string_truncate(variable_value, 40)!r}. "
                f"Allowed types: {types_str}."
            )
        )
