import logging
from pymongo import MongoClient
from loggers.loggers import get_logger
from Config.database.DB_Config import MONGO_URI, DB_NAME

logger = get_logger("MONITOR_MANAGER")

def get_db_connection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        logger.info("MongoDB connection established Successfully")
        return db
    except Exception as e:
        logger.debug(f"An error occurred while connecting to the database: {e}")
        return None

# if __name__ == "__main__":
#     get_db_connection()    