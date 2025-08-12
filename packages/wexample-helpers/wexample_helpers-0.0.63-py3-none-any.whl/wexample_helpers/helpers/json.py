import json
import os
from typing import Any, Dict, List, Union


def json_load(path: str) -> Union[List[Any], Dict[Any, Any]]:
    with open(path, "r") as f:
        return json.load(f)


def json_load_if_valid(path: str) -> Any | bool:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return False
    return False


def json_parse_if_valid(json_data: str, default: any = False) -> Any:
    try:
        return json.loads(json_data)
    except:
        return default
