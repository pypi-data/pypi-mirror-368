import pdb
from typing import Optional

from wexample_helpers.debug.abstract_debug import AbstractDebug


class DebugBreakpoint(AbstractDebug):
    def __init__(self, message: Optional[str] = None):
        self.message = message
        super().__init__()

    def collect_data(self) -> None:
        # No data collection needed for breakpoint
        pass

    def print(self) -> None:
        if self.message:
            print(f"\n Debug breakpoint: {self.message}")
            print("Commands:")
            print("  p variable  : Print variable")
            print("  n          : Next line")
            print("  c          : Continue execution")
            print("  q          : Quit")
            print("  h          : Help (more commands)")

        pdb.set_trace()
