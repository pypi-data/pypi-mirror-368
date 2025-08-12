from types import TracebackType
from typing import List, TYPE_CHECKING, Optional

from wexample_helpers.enums.debug_path_style import DebugPathStyle

if TYPE_CHECKING:
    from wexample_helpers.classes.trace_frame import TraceFrame


def trace_print(
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    truncate_stack: int = 0,
    paths_map: Optional[dict] = None
) -> None:
    print(trace_format(
        trace_get_frames(
            skip_frames=truncate_stack,
            path_style=path_style,
            paths_map=paths_map
        )
    ))


def trace_get_traceback_frames(
    traceback: TracebackType,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: Optional[dict] = None
) -> List["TraceFrame"]:
    """Convert exception traceback frames to TraceFrame objects."""
    from wexample_helpers.classes.trace_frame import TraceFrame

    frames = []
    current = traceback
    while current is not None:
        frame = current.tb_frame
        code = None
        if frame.f_code.co_filename != "<string>":
            try:
                with open(frame.f_code.co_filename, 'r') as f:
                    lines = f.readlines()
                    if 0 <= current.tb_lineno - 1 < len(lines):
                        code = lines[current.tb_lineno - 1]
            except (IOError, IndexError):
                pass

        trace_frame = TraceFrame(
            filename=frame.f_code.co_filename,
            lineno=current.tb_lineno,
            function=frame.f_code.co_name,
            code=code,
            path_style=path_style,
            paths_map=paths_map
        )
        frames.append(trace_frame)
        current = current.tb_next

    return frames


def trace_get_frames(
    skip_frames: int = 0,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: Optional[dict] = None
) -> List["TraceFrame"]:
    import inspect
    """Convert stack frames to TraceFrame objects."""
    from wexample_helpers.classes.trace_frame import TraceFrame

    frames = []
    for frame in inspect.stack()[1 + skip_frames:]:
        trace_frame = TraceFrame(
            filename=frame.filename,
            lineno=frame.lineno,
            function=frame.function,
            code=frame.code_context[0] if frame.code_context else None,
            path_style=path_style,
            paths_map=paths_map
        )
        frames.append(trace_frame)

    frames.reverse()
    return frames


def trace_format(
    traceback_frames: List["TraceFrame"]
) -> str:
    """Format a list of TraceFrame objects and optional exception information."""
    parts = [str(frame) for frame in traceback_frames]

    return '\n'.join(parts)
