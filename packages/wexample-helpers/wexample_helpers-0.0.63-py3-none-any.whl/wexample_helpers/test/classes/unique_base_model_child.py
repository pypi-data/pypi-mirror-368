from pydantic import Field
from wexample_helpers.classes.unique_base_model import UniqueBaseModel


class UniqueBaseModelChild(UniqueBaseModel):
    """A valid child class of UniqueBaseModel."""
    
    name: str = Field(default="test_child")
    value: int = Field(default=42)
    description: str = Field(default="A test child class")
