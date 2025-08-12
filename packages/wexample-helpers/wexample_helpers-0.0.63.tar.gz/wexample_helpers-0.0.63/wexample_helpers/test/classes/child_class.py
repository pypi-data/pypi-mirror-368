from wexample_helpers.test.classes.parent_class import ParentClass

class ChildClass(ParentClass):
    def __init__(self, child_value="child_default", parent_value="parent_default"):
        super().__init__(parent_value=parent_value)
        self.child_value = child_value
        
    def child_method(self):
        return f"{self.child_value} - {self.parent_value}"
