import configparser
from pathlib import Path
import json
from utils.logger.loggers import SingletonLogger

class CaseTemplateLoader:
    _logger = SingletonLogger.get_logger('appLogger')

    @staticmethod
    def load_case_template():
        """Load the case template from a JSON file, where the file name is specified in core_config.ini based on the environment."""
        CaseTemplateLoader._logger.info("Loading case template using environment-based config")
        try:
            # Load the config file
            project_root = Path(__file__).resolve().parents[2]
            config_path = project_root / 'config' / 'core_config.ini'
            config = configparser.ConfigParser()
            config.read(str(config_path))

            # Get the current environment
            if 'environment' not in config or 'current' not in config['environment']:
                raise KeyError("Missing [environment] section or 'current' key in core_config.ini")

            env = config['environment']['current'].lower()
            section = f'case_template_{env}'

            if section not in config:
                raise KeyError(f"Missing section [{section}] in config file.")

            # Read the template name
            template_name = config[section].get('template_name', '')
            if not template_name:
                raise ValueError(f"No template_name specified in [{section}] section")

            # Construct the path to the JSON file
            json_file_path = project_root / 'JSON_Templates' / f'{template_name}.json'

            # Read the JSON file
            with open(json_file_path, 'r') as file:
                template_data = json.load(file)

            CaseTemplateLoader._logger.info(f"Successfully loaded case template '{template_name}' for environment {env}")
            return template_data
        except FileNotFoundError:
            CaseTemplateLoader._logger.error(f"Case template JSON file not found at {json_file_path}")
            raise
        except json.JSONDecodeError as json_err:
            CaseTemplateLoader._logger.error(f"Error decoding JSON file: {json_err}")
            raise
        except KeyError as key_err:
            CaseTemplateLoader._logger.error(f"Configuration error: {key_err}")
            raise
        except Exception as err:
            CaseTemplateLoader._logger.error(f"Unexpected error loading case template: {err}")
            raise