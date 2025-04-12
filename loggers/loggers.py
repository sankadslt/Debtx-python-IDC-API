# import logging
# import logging.config
# import os

# # Load logger configuration from loggers.ini
# config_file = os.path.join(os.path.dirname(__file__), "loggers.ini")
# logging.config.fileConfig(config_file)

# def get_logger(name: str) -> logging.Logger:
#     return logging.getLogger(name)

import logging
from logging import config

from utils.get_roots_paths.get_roots_paths import get_logger_filePath


def setup_logging():
    config_file = get_logger_filePath()

    try:
        config.fileConfig(config_file)
    except Exception as e:
        print(f"Error setting up logging: {e}")

def get_logger(logger_name):
    """Retrieve a logger by name."""
    return logging.getLogger(logger_name)

# Setup logging on module import
setup_logging()