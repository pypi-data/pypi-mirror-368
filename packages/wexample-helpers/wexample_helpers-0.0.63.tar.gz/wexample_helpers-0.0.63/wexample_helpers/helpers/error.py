from typing import Optional, List

from wexample_helpers.classes.trace_frame import TraceFrame
from wexample_helpers.enums.debug_path_style import DebugPathStyle
from wexample_helpers.enums.error_truncate_rule import ErrorTruncateRules
from wexample_helpers.helpers.trace import trace_get_traceback_frames


def error_get_truncate_index(frames: List[TraceFrame], error: Exception) -> int:
    """Returns the index where to truncate the trace based on error type. Returns -1 if no truncation needed."""
    error_module = error.__class__.__module__

    for rule_type in ErrorTruncateRules:
        if error_module.startswith(rule_type.module_prefix):
            rule = rule_type.rule

            if rule.truncate_stack_count is not None:
                return min(rule.truncate_stack_count, len(frames))

            for i, frame in enumerate(frames):
                filename = frame.filename

                if rule.truncate_after_module and rule.truncate_after_module in filename:
                    return i + 1

                if rule.truncate_after_file and filename.endswith(rule.truncate_after_file):
                    return i + 1

    return -1


def error_format(
    error: Optional[Exception] = None,
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    paths_map: Optional[dict] = None,
) -> str:
    from wexample_helpers.helpers.trace import trace_format

    # Get frames from the exception traceback
    frames = trace_get_traceback_frames(
        error.__traceback__,
        path_style=path_style,
        paths_map=paths_map
    )
    truncate_index = error_get_truncate_index(frames, error)
    
    if truncate_index != -1:
        frames = frames[:truncate_index]
    
    # Then print the formatted traceback
    return f"{trace_format(frames)}\n{type(error).__name__}: {error}"
