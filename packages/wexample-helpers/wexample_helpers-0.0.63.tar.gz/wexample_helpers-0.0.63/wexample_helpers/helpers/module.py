from typing import Optional, Type, List, Dict

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def module_load(file_path: "Path"):
    import importlib
    import os

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create spec for {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_collect_classes(
        module,
        base_class: Optional[Type] = None,
        skip_prefixes: Optional[List[str]] = None
) -> Dict[str, Type]:
    import inspect

    """
    Collects non-abstract classes from a module, optionally filtering by base class and prefix.

    Args:
        module: The module to inspect.
        base_class: Optional base class to filter by.
        skip_prefixes: List of prefixes for class names to skip (e.g., ['Abstract']).

    Returns:
        Dictionary of class name to class object.
    """
    module_name = module.__name__
    collected: Dict[str, Type] = {}

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module_name:
            continue
        if inspect.isabstract(obj):
            continue
        if skip_prefixes and any(name.startswith(p) for p in skip_prefixes):
            continue
        if base_class and not issubclass(obj, base_class):
            continue
        collected[name] = obj

    return collected
