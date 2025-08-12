from enum import Enum
from typing import Optional


class ErrorTruncateRule:
    def __init__(
        self,
        truncate_after_module: Optional[str] = None,
        truncate_after_file: Optional[str] = None,
        truncate_stack_count: Optional[int] = None
    ):
        self.truncate_after_module = truncate_after_module
        self.truncate_after_file = truncate_after_file
        self.truncate_stack_count = truncate_stack_count


class ErrorTruncateRules(Enum):
    PYDANTIC = ("pydantic.", ErrorTruncateRule(truncate_after_module="pydantic"))

    def __init__(self, module_prefix: str, rule: ErrorTruncateRule):
        self.module_prefix = module_prefix
        self.rule = rule
