from typing import Optional, Type
from pydantic import BaseModel, Field, PrivateAttr
from .pydantic_circular_service import Service


class BaseKernel(BaseModel):
    """Base kernel class that defines common kernel behavior."""
    
    name: str = Field(description="Kernel name")
    debug: bool = Field(default=False)
    
    # Private service instance
    _service: Optional[Service] = PrivateAttr(default=None)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create and initialize service with the service class
        self._service = self.get_service_class()(name=f"{self.name}_service")
        self._service.initialize(self)
    
    @property
    def service(self) -> Service:
        """Get the managed service."""
        return self._service
    
    @classmethod
    def get_service_class(cls) -> Type[Service]:
        """Get the service class to instantiate. Can be overridden by subclasses."""
        return Service
