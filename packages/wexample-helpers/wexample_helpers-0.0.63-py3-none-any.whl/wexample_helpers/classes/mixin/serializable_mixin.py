from typing import TypeVar

from wexample_helpers.const.types import StringKeysDict

T = TypeVar("T", bound="SerializableMixin")


class SerializableMixin:
    def serialize(self) -> StringKeysDict:
        return {}

    def hydrate(self, data: StringKeysDict) -> None:
        pass
