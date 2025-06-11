from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import threading
from utils.config_loader_db import config

class MongoDBClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MongoDBClient, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        mongo_uri = config.get_env_value("mongodb", "uri")
        db_name = config.get_env_value("mongodb", "db_name")

        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        
mongo_client = MongoDBClient()
db = mongo_client.db        
    
