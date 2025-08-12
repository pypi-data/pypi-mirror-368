from typing import Optional, List
from .base_mixin import BaseMixin


class PublicFieldsMixin(BaseMixin):
    """Mixin providing public fields template."""

    name: str
    tags: List[str]
    description: Optional[str]
    version: str = "1.0.0"
