from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from utils.logger.loggers import get_logger
from utils.custom_exceptions.cust_exceptions import NoValidDataError
from openAPI_IDC.coreFunctions.config_manager import get_config  # Ensure this function is working properly

logger = get_logger("DB_Logger")

def get_db_connection():
    """Retrieve database connection from the hash map."""
    try:
        # Fetch database configuration from the hash map
        db_config = get_config("database","database")
        
        logger.info(f"Database Config:{db_config}")

        if not db_config:
            raise NoValidDataError("DATABASE configuration not found in hash map.")

        # Retrieve MongoDB connection details
        mongo_uri = db_config.get("mongo_uri", "").strip()
        db_name = db_config.get("db_name", "").strip()

        # Ensure values are valid
        if not mongo_uri or not db_name:
            raise NoValidDataError("Invalid MongoDB URI or database name.")
    
        # Connect to MongoDB
        client = MongoClient(mongo_uri,serverSelectionTimeoutMS=5000)
        
        client.server_info()  # Trigger an exception if the connection fails
        db = client[db_name]
        logger.info(f"Connected to MongoDB successfully | Database name: {db_name}")
        return db

    except NoValidDataError:
        logger.error("No valid data found")
        return False

    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return False