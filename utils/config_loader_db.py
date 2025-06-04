from pathlib import Path
import configparser
import threading
import ast

class ConfigLoader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigLoader, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._config = configparser.ConfigParser()

        # Get path to core_config.ini
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[1]
        core_config_file_path = project_root / "config" / "core_config.ini"

        if not core_config_file_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {core_config_file_path}")

        self._config.read(core_config_file_path)

        # Read active environment from [env] section
        try:
            self.environment = self._config.get("environment", "current")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise RuntimeError("Missing [environment] section or 'current' key in config file") from e

    def get_env_value(self, section_prefix, key):
        section = f"{section_prefix}_{self.environment}"
        if not self._config.has_section(section):
            raise KeyError(f"Missing section: [{section}] in config.")
        if not self._config.has_option(section, key):
            raise KeyError(f"Missing key '{key}' in section [{section}]")
        return self._config.get(section, key)

    def get_value(self, section: str, key: str) -> str:
        if not self._config.has_section(section):
            raise KeyError(f"Missing section: [{section}] in config.")
        if not self._config.has_option(section, key):
            raise KeyError(f"Missing key '{key}' in section [{section}]")
        return self._config.get(section, key)

# Shared instance
config = ConfigLoader()