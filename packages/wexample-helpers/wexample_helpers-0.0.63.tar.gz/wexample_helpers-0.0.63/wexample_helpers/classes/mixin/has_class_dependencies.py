from typing_extensions import List, Any

from wexample_helpers.helpers.polyfill import polyfill_register_global


class HasClassDependencies:
    @classmethod
    def get_class_dependencies(cls) -> List[Any]:
        """
        Return a list of class dependencies, basically the classes used by properties which are only defined for type checking, with quotes,
        this function can be used to import dependencies before rebuilding class
        """
        return []

    @classmethod
    def import_dependencies_and_rebuild(cls):
        import sys

        polyfill_register_global(
            cls.get_class_dependencies(),
            vars(sys.modules[cls.__module__])
        )
        cls.model_rebuild()
