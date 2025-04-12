from pymongo import MongoClient
# from config.database.DB_Config import MONGO_URI,DB_NAME
from loggers.loggers import get_logger
import configparser
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from utils.get_roots_paths.get_roots_paths import get_config_filePath
import os

logger = get_logger("Settlement_Manager")
def get_db_connection():
    """
    Establishes a connection to the MongoDB database using the configuration file.

    - Reads the MongoDB URI and database name from the databaseConfig.ini file.
    - Validates the presence of the configuration file and required fields.
    - Establishes a connection to the MongoDB database and returns the database object.

    :return: MongoDB database object.
    :raises Exception: If the configuration file is missing or connection fails.
    """
    try:
        config_path = get_config_filePath()  # Get the path to the config file
        logger.info(f"Reading configuration file from: {config_path}")  # Debugging log
        if not os.path.exists(config_path):
            logger.error(f"Configuration file '{config_path}' not found.")
            raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

        config = configparser.ConfigParser()
        config.read(config_path)

        if 'MONGODB' not in config:
            logger.error("'MONGODB' section not found in databaseConfig.ini")
            raise ValueError("'MONGODB' section not found in databaseConfig.ini")

        mongo_uri = config['MONGODB'].get('MONGO_URI', '').strip()
        db_name = config['MONGODB'].get('DATABASE_NAME', '').strip()

        if not mongo_uri or not db_name:
            logger.error("Missing MONGO_URI or DATABASE_NAME in databaseConfig.ini")
            raise ValueError("Missing MONGO_URI or DATABASE_NAME in databaseConfig.ini")

        client = MongoClient(mongo_uri)
        db = client[db_name]
        logger.info("Connected to MongoDB successfully.")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise DatabaseError(f"Error connecting to MongoDB: {e}")
    
    
# if __name__ == "__main__":
#     get_db_connection()
