from typing import Any


class MultipleBaseModelInheritanceError(Exception):
    """Exception raised when multiple inheritance of BaseModel is detected."""

    def __init__(self, class_instance: Any):
        super().__init__(
            f"Multiple inheritance of BaseModel is not allowed in class '{class_instance.__name__}'."
        )
