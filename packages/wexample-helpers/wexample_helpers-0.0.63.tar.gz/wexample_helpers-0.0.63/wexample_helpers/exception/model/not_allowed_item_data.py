from typing import List, Optional

from wexample_helpers.exception.undefined_exception import ExceptionData


class NotAllowedItemData(ExceptionData):
    """Data model for exceptions related to not allowed items."""
    item_type: str
    item_value: Optional[str] = None
    allowed_values: List[str] = []
    is_missing: bool = False
