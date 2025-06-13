import configparser
from pathlib import Path
from utils.logger.loggers import SingletonLogger

SingletonLogger.configure()

class ServerConfigLoader:
    _logger = SingletonLogger.get_logger('appLogger')

    @staticmethod
    def load_server_config():
        """Load server host and port from a unified section based on environment"""
        ServerConfigLoader._logger.info("Loading server host and port using environment-based config")
        try:
            project_root = Path(__file__).resolve().parents[1]
            config_path = project_root / 'config' / 'core_config.ini'
            config = configparser.ConfigParser()
            config.read(str(config_path))

            # Validate environment
            if 'environment' not in config or 'current' not in config['environment']:
                raise KeyError("Missing [environment] section or 'current' key in core_config.ini")

            env = config['environment']['current'].lower()

            # Load host and port from the combined section
            section = f'server_host_port_{env}'
            if section not in config:
                raise KeyError(f"Missing section [{section}] in config file.")

            host = config[section].get('host', '').strip()
            port_str = config[section].get('port', '').strip()

            if not host:
                raise ValueError(f"Invalid or missing 'host' in [{section}] section")
            if not port_str.isdigit():
                raise ValueError(f"Invalid or missing 'port' in [{section}] section")

            port = int(port_str)

            ServerConfigLoader._logger.info(f"Successfully loaded server config for env '{env}': host={host}, port={port}")
            return host, port

        except Exception as e:
            ServerConfigLoader._logger.error(f"Error loading server config: {e}")
            raise
