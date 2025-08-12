from pathlib import Path
from typing import Union
from pydantic import validator

from wexample_helpers.classes.local_file_path import LocalFilePath


class LocalFilePathExisting(LocalFilePath):
    """A wrapper for paths that guarantees the path exists at runtime."""

    @validator('path')
    def validate_path_exists(cls, value: Union[str, Path], values: dict) -> Path:
        """Validate that the path exists in addition to parent validation."""
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
            
        # Let parent class handle type validation
        return super().validate_path(path, values)
