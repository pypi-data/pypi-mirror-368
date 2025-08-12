class SecondParent:
    def __init__(self, second_value="default_second"):
        self.second_value = second_value
        
    def second_method(self):
        return f"Second parent method with value: {self.second_value}"
