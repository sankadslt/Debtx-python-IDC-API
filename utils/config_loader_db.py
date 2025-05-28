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
        config = configparser.ConfigParser()

        # Find project root (you can adjust if needed)
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[1]
        core_config_file_path = project_root / "config" / "core_config.ini"

        if not core_config_file_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {core_config_file_path}")

        config.read(core_config_file_path)

        # Environment
        self.environment = config.get("ENVIRONMENT", "DATABASE")

        # MongoDB URI and DB name
        mongo_uri_with_db_name = config.get("MONGODB", self.environment)
        self.mongo_uri, self.database_name = mongo_uri_with_db_name.rsplit("/", 1)
        
        # Interaction ID Numbers
        interaction_ids_raw = config.get("INTERACTION_ID_NUMBERS", "INTERACTION_ID_NUMBERS")
        self.interaction_id_numbers = ast.literal_eval(interaction_ids_raw) if interaction_ids_raw else []

# Create a shared instance on import
config = ConfigLoader()
