from pydantic import BaseModel


class UniqueBaseModel(BaseModel):
    """
    Abstract base class that prevents multiple inheritance of BaseModel.

    During the initialization of a subclass, the __init_subclass__ method inspects
    the immediate parent classes to ensure that no more than one class derived from
    BaseModel is present. If multiple BaseModel-derived classes are detected, a
    MultipleBaseModelInheritanceError is raised.

    This class is abstract and cannot be instantiated directly.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Count the number of direct base classes that are subclasses of BaseModel.
        base_model_count = sum(1 for base in cls.__bases__ if issubclass(base, BaseModel))
        if base_model_count > 1:
            from wexample_helpers.errors.multiple_base_model_inheritance_error import MultipleBaseModelInheritanceError

            raise MultipleBaseModelInheritanceError(cls)
