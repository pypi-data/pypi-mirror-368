from typing import List, Optional

from wexample_helpers.exception.undefined_exception import UndefinedException
from wexample_helpers.exception.mixin.not_allowed_item_mixin import NotAllowedItemMixin
from wexample_helpers.exception.model.not_allowed_item_data import NotAllowedItemData


class NotAllowedItemException(UndefinedException, NotAllowedItemMixin):
    """Base exception for cases where an item is not allowed or not provided.
    
    This exception should be used when:
    1. A specific item value is not in a list of allowed values
    2. A required item was not provided at all
    """
    error_code: str = "NOT_ALLOWED_ITEM"

    def __init__(
            self,
            item_type: str,
            item_value: Optional[str] = None,
            allowed_values: List[str] = None,
            cause: Optional[Exception] = None,
            previous: Optional[Exception] = None,
            message: Optional[str] = None
    ):
        if allowed_values is None:
            allowed_values = []

        # Create structured data using Pydantic model
        data_model = NotAllowedItemData(
            item_type=item_type,
            item_value=item_value,
            allowed_values=allowed_values,
            is_missing=item_value is None
        )

        # Store attributes as instance attributes
        self.item_type = item_type
        self.item_value = item_value
        self.allowed_values = allowed_values
        self.is_missing = item_value is None

        # Generate message using the mixin method
        message = message or self.format_not_allowed_item_message(
            item_type=item_type,
            item_value=item_value,
            allowed_values=allowed_values
        )

        super().__init__(
            message=message,
            data=data_model.model_dump(),
            cause=cause,
            previous=previous
        )
