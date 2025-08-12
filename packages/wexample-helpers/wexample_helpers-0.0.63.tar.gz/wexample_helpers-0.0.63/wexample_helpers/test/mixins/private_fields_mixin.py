from datetime import datetime
from typing import Dict, Any


class PrivateFieldsMixin:
    """Mixin providing private attributes template."""
    _metadata: Dict[str, Any]
    _created_at: datetime
    _secret_key: str = "default-key"

    def __init__(self):
        self._created_at = datetime.now()
        self._metadata = {}

    def get_metadata(self) -> Dict[str, Any]:
        """Safe access to private metadata."""
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any) -> None:
        """Safely set metadata value."""
        self._metadata[key] = value

    @property
    def created_at(self) -> datetime:
        """Read-only access to creation time."""
        return self._created_at
