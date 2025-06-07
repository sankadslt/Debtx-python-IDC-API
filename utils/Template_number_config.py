import configparser
from pathlib import Path
from utils.logger.loggers import SingletonLogger

SingletonLogger.configure()

class TemplateConfigLoader:
    _logger = SingletonLogger.get_logger('templateLoader')

    @staticmethod
    def load_template_numbers():
        """Load template numbers list from core_config.ini"""
        try:
            project_root = Path(__file__).resolve().parents[1]
            config_path = project_root / 'config' / 'core_config.ini'

            config = configparser.ConfigParser()
            config.read(str(config_path))

            if 'template_numbers' not in config:
                raise KeyError("Missing [template_numbers] section in config file")

            raw_value = config['template_numbers'].get('template_numbers', '').strip()
            if not raw_value:
                raise ValueError("Missing 'template_numbers' key in [template_numbers] section")

            # Safely evaluate the list (assumes it is a Python-style list like [1,2,3,...])
            try:
                template_numbers = eval(raw_value)
                if not isinstance(template_numbers, list) or not all(isinstance(i, int) for i in template_numbers):
                    raise ValueError("Parsed template numbers are not a valid list of integers")
            except Exception as e:
                raise ValueError(f"Failed to parse template numbers: {e}")

            TemplateConfigLoader._logger.info(f"Loaded template numbers: {template_numbers}")
            return template_numbers

        except Exception as e:
            TemplateConfigLoader._logger.error(f"Error loading template numbers: {e}")
            raise
