import ast
import inspect
import re
from typing import Any, Dict, Iterable, List, Optional, Union, cast

from wexample_helpers.const.types import (
    AnyCallable,
    BasicValue,
    StringKeysDict,
    StringsList,
    Scalar,
)
from wexample_helpers.helpers.string import string_to_snake_case


def args_replace_one(
    arg_list: List[str],
    arg_name: str,
    value: Optional[Any] = None,
    is_flag: bool = False,
) -> Optional[str | bool]:
    previous = args_shift_one(arg_list=arg_list, arg_name=arg_name, is_flag=is_flag)

    args_push_one(arg_list=arg_list, arg_name=arg_name, value=value)

    return previous


def args_push_one(
    arg_list: List[str], arg_name: str, value: Optional[Any] = None
) -> None:
    arg_list.append(f"--{arg_name}")

    if value is not None:
        arg_list.append(str(value))


def args_shift_one(
    arg_list: List[str], arg_name: str, is_flag: bool = False
) -> Optional[str | bool]:
    """
    Alter arg list by removing arg names and returning arg value.
    Take arg name without dash, and remove args with any count of prefixed dashes.
    """
    arg_pattern = re.compile(r"(-+)" + re.escape(arg_name) + r"$")

    for i, arg in enumerate(arg_list):
        if isinstance(arg, str) and arg_pattern.match(arg):
            del arg_list[i]

            if is_flag:
                return True
            else:
                try:
                    next_value = arg_list.pop(i)
                    return next_value
                except IndexError:
                    return None
    return None


def args_split_arg_array(
    arg: Union[str, Iterable[str]], separator: str = ","
) -> StringsList:
    if not arg:
        return []

    if isinstance(arg, str):
        arg = re.sub(r'[\[\]"\']', "", arg)

        # The array was empty.
        if not arg:
            return []

        return [item.strip() for item in arg.split(separator)]
    elif isinstance(arg, Iterable):
        return [item.strip() for item in arg]


def args_convert_dict_to_snake_dict(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {string_to_snake_case(key): value for key, value in input_dict.items()}


def args_parse_dict(arg: str) -> StringKeysDict:
    arg_dict = args_parse_one(arg, {})

    if not isinstance(arg_dict, dict):
        return {}

    return arg_dict


def args_parse_list_or_strings_list(arg: str) -> StringsList:
    if arg.startswith("[") and arg.endswith("]"):
        return args_parse_list(arg)

    return arg.split()


def args_parse_list(arg: str) -> StringsList:
    arg_list = args_parse_one(arg, [])

    if not isinstance(arg_list, list):
        return []

    assert isinstance(arg_list, list)

    return cast(StringsList, arg_list)


def args_parse_one(argument: str, default: Optional[Any] = None) -> BasicValue:
    if argument is None or argument == "":
        return default

    try:
        parsed = ast.literal_eval(argument)
        if args_is_basic_value(parsed):
            return cast(BasicValue, parsed)
        return default
    except (ValueError, SyntaxError):
        return argument


def args_is_basic_value(value: Any) -> bool:
    """
    Check if the value is compatible with basic YAML types
    """

    if isinstance(value, Scalar):
        return True

    elif isinstance(value, list):
        return all(args_is_basic_value(item) for item in value)

    elif isinstance(value, dict):
        return all(
            isinstance(key, str) and args_is_basic_value(val)
            for key, val in value.items()
        )

    else:
        return False


def args_in_function(function: AnyCallable, arg_name: str) -> bool:
    return arg_name in inspect.signature(function).parameters
