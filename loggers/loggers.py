import logging
import logging.config
import os

# Load logger configuration from loggers.ini
config_file = os.path.join(os.path.dirname(__file__), "loggers.ini")
logging.config.fileConfig(config_file)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)