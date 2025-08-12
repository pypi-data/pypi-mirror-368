from typing import Union, Type, Any


def cli_make_clickable_path(path: str, short_title: Union[bool, str] = False) -> str:
    from pathlib import Path

    if isinstance(short_title, str):
        display_text = short_title
    elif short_title:
        display_text = Path(path).name
    else:
        display_text = path

    # \033]8;;file://{path}\033\\  : Link start
    # \033]8;;\033\\              : Link end
    return f"\033]8;;file://{path}\033\\{display_text}\033]8;;\033\\"


def cli_argument_convert_value(value: str, target_type: Type) -> Any:
    """
    Convert an argument value to the target type.
    """
    if target_type == bool:
        return value.lower() in ('true', 'yes', 'y', '1')
    elif target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    elif target_type == str:
        return value
    elif target_type == list:
        # Assume comma-separated values
        return [item.strip() for item in value.split(',')]
    else:
        # For custom types, try to use the constructor
        return target_type(value)
