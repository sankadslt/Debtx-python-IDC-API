import configparser
from pathlib import Path
from utils.logger.loggers import SingletonLogger

SingletonLogger.configure()

class ServerConfigLoader:
    _logger = SingletonLogger.get_logger('appLogger')

    @staticmethod
    def load_server_config():
        """Load server host and port based on environment from core_config.ini"""
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

            # Load port
            port_section = f'server_port_{env}'
            if port_section not in config:
                raise KeyError(f"Missing section [{port_section}] in config file.")
            port_str = config[port_section].get('port', '').strip()
            if not port_str.isdigit():
                raise ValueError(f"Invalid or missing 'port' in [{port_section}] section")
            port = int(port_str)

            # Load host
            host_section = f'server_host_{env}'
            if host_section not in config:
                raise KeyError(f"Missing section [{host_section}] in config file.")
            host = config[host_section].get('host', '').strip()
            if not host:
                raise ValueError(f"Invalid or missing 'host' in [{host_section}] section")

            ServerConfigLoader._logger.info(f"Successfully loaded server config for env '{env}': host={host}, port={port}")
            return host, port

        except Exception as e:
            ServerConfigLoader._logger.error(f"Error loading server config: {e}")
            raise
