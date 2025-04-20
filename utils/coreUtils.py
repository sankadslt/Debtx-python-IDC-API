from pathlib import Path
import configparser

# Public variable to store configuration values
config_values = {}

def load_config():
    # ------------------ READ CONFIG ------------------
    config = configparser.ConfigParser()

    # Get the current file path
    current_file = Path(__file__).resolve()

    # Locate the project root
    project_root = current_file.parents[1]
    print("Project root: ", project_root)

    # Construct the path to the coreConfig.ini file
    core_config_file_path = project_root / "Config" / "coreConfig.ini"
    print("Configuration file path: ", core_config_file_path)

    if not core_config_file_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {core_config_file_path}")

    # Read the coreConfig.ini file
    config.read(core_config_file_path)





    # Get the environment value
    try:
        extracted_environment = config.get("ENVIRONMENT", "DATABASE")
        config_values["environment"] = extracted_environment
    except configparser.NoSectionError:
        raise Exception("Missing environment section in configuration file.")
    except configparser.NoOptionError:
        raise Exception(f"No mongo environment found for {extracted_environment}.")

    try:
        mongo_uri_with_db_name = config.get("MONGODB", extracted_environment)
        # Check if MongoDB URI is not empty or null
        if not mongo_uri_with_db_name.strip():
            raise ValueError(f"{extracted_environment} MongoDB URI is empty or null.")
    except configparser.NoSectionError:
        raise Exception("Missing mongoDB section in configuration file.")
    except configparser.NoOptionError:
        raise KeyError(f"No mongoDB URI found for {extracted_environment}.")

    # Separate database name and mongo uri (by the last '/')
    extracted_mongo_uri, extracted_database_name = mongo_uri_with_db_name.rsplit("/", 1)
    config_values["mongo_uri"] = extracted_mongo_uri
    config_values["database_name"] = extracted_database_name
    
        # ------------------ API ------------------
    try:
        api_url = config.get("API", "api_url")
        if not api_url.strip():
            raise ValueError("API URL is empty or null.")
        config_values["api_url"] = api_url
    except configparser.NoSectionError:
        raise Exception("Missing API section in configuration file.")
    except configparser.NoOptionError:
        raise Exception("Missing api_url option under API section.")



    # Return the config_values global hash map
    return config_values