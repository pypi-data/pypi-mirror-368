from typing import Any, List, Sequence, Optional


def array_replace_value(
    array: Sequence[Any], search: Any, replacement: Any
) -> List[Any]:
    return [replacement if value == search else value for value in array]


def array_swap(two_items_array: List[Any], do_swap: bool) -> List[Any]:
    if do_swap:
        two_items_array.reverse()

        return two_items_array

    return two_items_array


def array_unique(array: Sequence[Any]) -> List[Any]:
    return list(set(array))

def array_dict_get_by(key: str, value: Any, list_of_dicts: List[dict]) -> Optional[dict]:
    """
    Retrieve a dictionary from a list of dictionaries based on a specific key-value pair.

    :param key: The key to search for in the dictionaries.
    :param value: The value to match for the specified key.
    :param list_of_dicts: The list of dictionaries to search.
    :return: The first dictionary that matches the key-value pair, or None if not found.
    """
    return next((d for d in list_of_dicts if d.get(key) == value), None)
