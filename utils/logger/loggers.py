from pathlib import Path

import logging

import logging.config

import configparser

 

from datetime import datetime

 

class SingletonLogger:

    _instances = {}

    _configured = False

 

    @classmethod

    def configure(cls):

        project_root = Path(__file__).resolve().parents[2]

        config_dir = project_root / 'config'

        corefig_path = config_dir / 'core_config.ini'

 

        if not corefig_path.exists():

            raise FileNotFoundError(f"Configuration file not found: {corefig_path}")

 

        config = configparser.ConfigParser()

        config.read(str(corefig_path))

 

        # Get current environment

        if 'environment' not in config or 'current' not in config['environment']:

            raise ValueError("Missing [environment] section or 'current' key in core_config.ini")

        environment = config['environment']['current'].lower()

 

        # Get logger path based on environment

        logger_section = f'logger_path_{environment}'

        if logger_section not in config or 'log_dir' not in config[logger_section]:

            raise ValueError(f"Missing 'log_dir' under section [{logger_section}]")

 

        log_dir = Path(config[logger_section]['log_dir'])

        log_dir.mkdir(parents=True, exist_ok=True)

 

        today_str = datetime.now().strftime("%Y%m%d")

 

        # Define separate log files

        log_file_info = log_dir / f"{today_str}_info.log"

        log_file_error = log_dir / f"{today_str}_error.log"

 

        # print(f"Logger Info Path: {log_file_info} (env: {environment})")

        # print(f"Logger Error Path: {log_file_error} (env: {environment})")

 

        # Load logger.ini with dynamic path

        logger_ini_path = config_dir / 'logger.ini'

        if not logger_ini_path.exists():

            raise FileNotFoundError(f"Logger configuration file not found: {logger_ini_path}")

 

        logging.config.fileConfig(

            str(logger_ini_path),

            defaults={

                'logfilename_info': str(log_file_info.as_posix()),

                'logfilename_error': str(log_file_error.as_posix())

            },

            disable_existing_loggers=False

        )

        cls._configured = True

 

    @classmethod

    def get_logger(cls, logger_name='appLogger'):

        if not cls._configured:

            raise ValueError("Logger not configured. Please call 'configure()' first.")

 

        if logger_name not in cls._instances:

            cls._instances[logger_name] = logging.getLogger(logger_name)

 

        return cls._instances[logger_name]

 

class MaxLevelFilter(logging.Filter):

    """

    Allows only log records with level <= max_level (DEBUG, INFO, WARNING go to info.log).

    """

    def __init__(self, level):

        super().__init__()

        self.max_level = logging._nameToLevel[level.upper()]

 

    def filter(self, record):

        return record.levelno <= self.max_level

 

class MinLevelFilter(logging.Filter):

    """

    Allows only log records with level >= min_level (ERROR, CRITICAL go to error.log).

    """

    def __init__(self, level):

        super().__init__()

        self.min_level = logging._nameToLevel[level.upper()]

 

    def filter(self, record):

        return record.levelno >= self.min_level