from utils.db import db
from utils.custom_exceptions.custom_exceptions import DatabaseConnectionError
from pymongo.errors import PyMongoError

async def get_next_case_id():
    try:
        last = await db["Case_details"].find_one(sort=[("case_id", -1)])
        return (last["case_id"] + 1) if last else 1
    
    except PyMongoError as e:
        raise DatabaseConnectionError("Failed to fetch latest case_id", extra={"error": str(e)})