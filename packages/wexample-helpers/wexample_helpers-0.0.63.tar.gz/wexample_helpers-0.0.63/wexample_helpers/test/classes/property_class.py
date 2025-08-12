class PropertyClass:
    def __init__(self):
        self._value = None
        
    @property
    def value(self):
        """Get the value."""
        return self._value
        
    @value.setter
    def value(self, new_value):
        """Set the value."""
        self._value = new_value
