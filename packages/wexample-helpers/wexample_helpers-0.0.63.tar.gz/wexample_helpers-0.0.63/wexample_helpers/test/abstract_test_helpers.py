from abc import ABC
from typing import Any, Callable, Dict, List, Tuple, Union, Type, Optional, Set

import pytest

from wexample_helpers.helpers.type import (
    type_validate_or_fail,
)


class AbstractTestHelpers(ABC):
    def _test_type_validate_or_fail(
        self,
        success_cases: list[Tuple[Any, Any]] = None,
        failure_cases: list[Tuple[Any, Any]] = None):
        # Success cases: should not raise exceptions
        for value, expected_type in (success_cases or []):
            type_validate_or_fail(
                value=value,
                allowed_type=expected_type,
            )

        # Failure cases: should raise TypeError
        for value, expected_type in (failure_cases or []):
            with pytest.raises(TypeError):
                type_validate_or_fail(
                    value=value,
                    allowed_type=expected_type,
                )
