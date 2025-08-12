class PydanticInheritanceConfig:
    """Simple configuration class with a basic property."""
    
    def __init__(self, environment: str = "development"):
        self._environment = environment
    
    @property
    def environment(self) -> str:
        """Get the current environment."""
        return self._environment
    
    @environment.setter
    def environment(self, value: str) -> None:
        """Set the current environment."""
        self._environment = value.lower()
