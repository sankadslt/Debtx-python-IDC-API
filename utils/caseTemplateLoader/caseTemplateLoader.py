import configparser
from pathlib import Path
import json
from utils.logger.loggers import SingletonLogger

class CaseTemplateLoader:
    _logger = SingletonLogger.get_logger('appLogger')

    @staticmethod
    def load_case_template(version=None):
        
        """Load the case template from a JSON file, where the file name is specified in core_config.ini."""
        CaseTemplateLoader._logger.info(f"Loading case template for version {version if version is not None else 'default'} using config")
        try:
            # Load the config file
            project_root = Path(__file__).resolve().parents[2]
            config_path = project_root / 'config' / 'core_config.ini'
            config = configparser.ConfigParser()
            config.read(str(config_path))


            # If no version is specified, use the default version from the ini file
            if version is None:
                if 'case_template' not in config:
                    raise KeyError("Missing [case_template] section in core_config.ini")
                version = int(config['case_template'].get('default_version', '1'))  # Default to 1 if not specified

            # Determine the section based on the version
            section = f'case_template_v{version}'
            if section not in config:
                raise KeyError(f"Missing [{section}] section in core_config.ini")

            # Read the template name
            template_name = config[section].get('template_name', '')
            if not template_name:
                raise ValueError(f"No template_name specified in [{section}] section")

            # Construct the path to the JSON file
            json_file_path = project_root / 'JSON_Templates' / f'{template_name}.json'

            # Read the JSON file
            with open(json_file_path, 'r') as file:
                template_data = json.load(file)

            CaseTemplateLoader._logger.info(f"Successfully loaded case template '{template_name}' for version {version}")
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