from pathlib import Path
from typing import Union, Optional
from pydantic import BaseModel, Field, validator

class LocalFilePath(BaseModel):
    """Base class for handling local file paths with type checking capabilities."""
    
    path: Path = Field(description="The path to the file or directory")
    check_is_file: Optional[bool] = Field(
        default=None,
        description="If True, verify path is a file. If False, verify it's a directory. If None, accept either."
    )
    
    @validator('path')
    def validate_path(cls, value: Union[str, Path], values: dict) -> Path:
        """Validate the path and convert to Path object if needed."""
        path = Path(value)
        check_is_file = values.get('check_is_file')
        
        if path.exists():
            if check_is_file is True and not path.is_file():
                raise ValueError(f"Path exists but is not a file: {path}")
            elif check_is_file is False and not path.is_dir():
                raise ValueError(f"Path exists but is not a directory: {path}")
        
        return path
    
    def __str__(self) -> str:
        return str(self.path)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(str(self.path))})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LocalFilePath):
            return self.path == other.path
        return self.path == other
    
    # Delegate common Path methods
    def is_file(self) -> bool:
        return self.path.is_file()
    
    def is_dir(self) -> bool:
        return self.path.is_dir()
    
    def exists(self) -> bool:
        return self.path.exists()
    
    def absolute(self) -> Path:
        return self.path.absolute()
    
    def resolve(self) -> Path:
        return self.path.resolve()
