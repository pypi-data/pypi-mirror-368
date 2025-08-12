from typing import Optional, Dict

from wexample_helpers.debug.abstract_debug import AbstractDebug
from wexample_helpers.enums.debug_path_style import DebugPathStyle
from wexample_helpers.helpers.trace import trace_print


class DebugTrace(AbstractDebug):
    def __init__(
            self,
            path_style: DebugPathStyle = DebugPathStyle.FULL,
            truncate_stack: int = 0,
            paths_map: Optional[Dict] = None,
            message: Optional[str] = None
    ):
        self.path_style = path_style
        self.truncate_stack = truncate_stack
        self.paths_map = paths_map
        self.message = message
        super().__init__()

    def collect_data(self) -> None:
        # No data collection needed for trace
        pass

    def print(self) -> None:
        if self.message:
            print(f"\n {self.message}")

        trace_print(
            truncate_stack=self.truncate_stack,
            path_style=self.path_style,
            paths_map=self.paths_map
        )
