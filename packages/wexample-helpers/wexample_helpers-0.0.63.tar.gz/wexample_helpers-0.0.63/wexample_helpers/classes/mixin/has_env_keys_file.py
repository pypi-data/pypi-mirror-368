from wexample_helpers.classes.mixin.has_env_keys import HasEnvKeys


class HasEnvKeysFile(HasEnvKeys):
    """Mixin for classes that need to load env from files."""

    def _init_env_file(self, file_path: str) -> None:
        """
        Load environment variables from a file and validate them.
        
        Args:
            file_path: Path to the .env file
        """
        from dotenv import load_dotenv, dotenv_values

        load_dotenv(file_path)
        self.env_config.update(dotenv_values(file_path))
        self._validate_env_keys()

    def _init_env_file_yaml(self, file_path: str) -> None:
        from wexample_helpers_yaml.helpers.yaml_helpers import yaml_read_dict

        self.env_config.update(yaml_read_dict(file_path))
        self._validate_env_keys()
