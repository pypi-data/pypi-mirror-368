from typing import List, Dict, Any

from wexample_helpers.const.types import StringsList


class HasEnvKeys:
    """Base mixin for environment variable validation."""

    env_config: Dict[str, str | None] = {}

    def __init__(self, **kwargs) -> None:
        self.env_config = {}

    def get_expected_env_keys(self) -> List[str]:
        """
        Returns a list of required environment variable keys.
        Should be overridden by child classes.
        """
        return []

    def _validate_env_keys(self) -> None:
        """
        Validates that all required environment variables are set.
        Raises MissingRequiredEnvVarError if any required variable is missing.
        """
        missing_keys = self._get_missing_env_keys(
            self.get_expected_env_keys()
        )

        if missing_keys:
            from wexample_helpers.errors.missing_required_env_var_error import MissingRequiredEnvVarError

            raise MissingRequiredEnvVarError(missing_keys)

    def _get_missing_env_keys(self, required_keys: StringsList) -> StringsList:
        """Check for missing environment variables in both os.environ and _env_values."""
        import os

        missing = []
        for key in required_keys:
            if not os.environ.get(key) and key not in self.env_config:
                missing.append(key)
        return missing

    def _init_env(self, env_dict: Dict[str, str]) -> None:
        """
        Initialize environment values from an external source.

        Args:
            env_dict: Dictionary of environment variables
        """
        self.env_config = env_dict
        self._validate_env_keys()

    def get_env_parameter(self, key: str, default: Any = None) -> Any:
        from wexample_helpers.errors.key_not_found_error import KeyNotFoundError

        if not key in self.env_config:
            if default is not None:
                return default
            
            raise KeyNotFoundError(
                message=f'Environment variable is not defined',
                key=key,
                available_keys=list(self.env_config.keys())
            )
        return self.env_config[key]
