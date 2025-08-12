import os
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Callable, List

from wexample_file.const.types import PathOrString
from wexample_helpers.helpers.file import file_read

AnyCallable = Callable[..., Any]


def directory_remove_tree_if_exists(directory: PathOrString) -> None:
    """Remove a directory and all its contents if it exists."""
    p = Path(directory)
    if p.exists():
        shutil.rmtree(p)


@contextmanager
def directory_execute_inside(target_dir: PathOrString):
    """
    Context manager to execute code inside a specific directory.

    Usage:
        with directory_execute_inside('path/to/dir'):
            # code here
    """
    original_dir = os.getcwd()
    p = Path(target_dir)
    os.chdir(p)
    try:
        yield
    finally:
        os.chdir(original_dir)


def directory_execute_inside_fn(target_dir: PathOrString, callback: AnyCallable) -> Any:
    """Execute a callback inside the target directory and return its result."""
    with directory_execute_inside(target_dir):
        return callback()


def directory_get_base_name(path: PathOrString) -> str:
    """Return the base name of a path (last component)."""
    p = Path(path)
    return os.path.basename(os.path.normpath(os.fspath(p)))


def directory_get_parent_path(path: PathOrString) -> str:
    """Return the parent directory path with trailing separator."""
    p = Path(path)
    parent = os.path.dirname(os.path.normpath(os.fspath(p)))
    return parent + os.sep if parent else os.sep


def directory_empty_dir(dir_path: PathOrString) -> None:
    """Remove all contents within a directory, but keep the directory itself."""
    p = Path(dir_path)
    if not p.is_dir():
        raise NotADirectoryError(f"{p!r} is not a directory.")
    for item in os.listdir(p):
        item_path = os.path.join(p, item)
        if os.path.isdir(item_path) and not os.path.islink(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)


def directory_list_files(dir_path: PathOrString) -> List[str]:
    """List all files in directory and subdirectories, sorted alphabetically."""
    p = Path(dir_path)
    file_paths: List[str] = []
    for root, _, files in os.walk(p):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                file_paths.append(full_path)
    return file_paths


def directory_aggregate_all_files(file_paths: List[PathOrString]) -> str:
    """Aggregate contents of the given list of file paths."""
    return os.linesep.join(file_read(os.fspath(Path(fp))) for fp in file_paths)


def directory_aggregate_all_files_from_dir(dir_path: PathOrString) -> str:
    """Aggregate contents of all files in a directory and its subdirectories."""
    return directory_aggregate_all_files(directory_list_files(dir_path))
