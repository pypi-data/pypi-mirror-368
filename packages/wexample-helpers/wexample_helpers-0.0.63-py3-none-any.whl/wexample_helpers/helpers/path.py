import os
from pathlib import Path


def path_resolve_from(path: str, from_cwd: str) -> str:
    """
    Resolves a path relative to a given directory, even if the paths don't exist.

    Args:
        path (str): The path to resolve
        from_cwd (str): The directory to resolve from

    Returns:
        str: The absolute resolved path
    """
    # Convert both inputs to Path objects
    path_obj = Path(path)
    from_cwd_obj = Path(from_cwd)

    # If path is already absolute, just normalize it
    if path_obj.is_absolute():
        return os.path.normpath(str(path_obj))

    # Make from_cwd absolute if it's not already
    if not from_cwd_obj.is_absolute():
        from_cwd_obj = Path(os.getcwd()) / from_cwd_obj

    # Join the paths and normalize
    resolved_path = from_cwd_obj / path_obj

    # Normalize the path (resolves '..' and '.')
    return os.path.normpath(str(resolved_path))
