from pydantic import BaseModel, Field, field_validator, computed_field, PrivateAttr
from typing import Optional, List, Dict, Union
from datetime import datetime, timedelta
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"

class PydanticAdvanced(BaseModel):
    """A more complex Pydantic model with various field types and features."""
    
    # Private attributes (using PrivateAttr)
    _secret_key: str = PrivateAttr(default="private")
    _created_at: datetime = PrivateAttr(default_factory=datetime.now)
    _internal_notes: List[str] = PrivateAttr(default_factory=list)
    
    # Public fields
    id: str = Field(description="Unique identifier")
    status: Status = Field(default=Status.PENDING)
    
    # Complex types
    metadata: Dict[str, Union[str, int, bool]] = Field(
        default_factory=dict,
        description="Arbitrary metadata"
    )
    
    # Field with validator
    score: float = Field(ge=0, le=100, description="Score between 0 and 100")
    
    @field_validator("score")
    def validate_score(cls, value: float) -> float:
        return round(value, 2)
    
    # Computed properties
    @computed_field
    @property
    def age(self) -> timedelta:
        return datetime.now() - self._created_at
        
    @property
    def is_active(self) -> bool:
        return self.status == Status.ACTIVE
        
    # Custom property with getter and setter
    @property
    def notes(self) -> List[str]:
        return self._internal_notes.copy()
        
    @notes.setter
    def notes(self, value: List[str]) -> None:
        self._internal_notes = [note.strip() for note in value]
        
    model_config = {
        "arbitrary_types_allowed": True
    }
