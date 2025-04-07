import configparser
import os
from utils.logger.loggers import get_logger
from utils.filePath.filePath import get_filePath

logger = get_logger("System_logger")

# Global dictionary to store hash maps
HASH_MAP = {}

# File paths
CONFIG_FILES = {
    "database": get_filePath("config_drs")
}

def read_ini_file(file_path):
    """Reads an INI file and returns a dictionary of its contents."""
    config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
    config.read(file_path)

    if not config.sections():
        logger.error(f"INI file {file_path} is empty or not formatted correctly.")
        return {}

    data = {section.lower(): dict(config.items(section)) for section in config.sections()}  # Convert section names to lowercase
    logger.info(f"INI file loaded: {file_path} -> {data}")  # Debugging line
    return data

def initialize_hash_maps():
    """Creates hash maps from INI files at startup."""
    global HASH_MAP
    for name, path in CONFIG_FILES.items():
        if os.path.exists(path):
            HASH_MAP[name] = read_ini_file(path)
            if HASH_MAP[name]:  
                logger.info(f"Hash map for {name} loaded successfully: {HASH_MAP[name]}")
            else:
                logger.error(f"Failed to load hash map for {name}.")
        else:
            logger.error(f"Configuration file {path} not found. Skipping...")
            return False

def get_config(category, key=None):
    """Retrieves configuration values from the hash map."""
    if key:
        return HASH_MAP.get(category, {}).get(key, None)
    return HASH_MAP.get(category, {})
