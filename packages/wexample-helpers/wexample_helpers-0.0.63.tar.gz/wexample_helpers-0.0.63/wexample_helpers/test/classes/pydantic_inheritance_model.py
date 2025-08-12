from pydantic import BaseModel, Field

from ..mixins.private_fields_mixin import PrivateFieldsMixin
from ..mixins.public_fields_mixin import PublicFieldsMixin


class PydanticInheritanceModel(PublicFieldsMixin, PrivateFieldsMixin, BaseModel):
    """Pydantic model combining both mixins with additional functionality."""

    enabled: bool = Field(default=True, description="Whether the instance is enabled")
    priority: int = Field(default=0, ge=0, le=100, description="Priority level (0-100)")

    def __init__(self, **data):
        BaseModel.__init__(self, **data)
        PrivateFieldsMixin.__init__(self)
        PublicFieldsMixin.__init__(self)

        # Initialize any mixin-specific stuff if needed
        self._metadata["initialized_at"] = self._created_at
