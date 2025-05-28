from utils.db import db
from utils.custom_exceptions.custom_exceptions import DatabaseConnectionError
from pymongo.errors import PyMongoError

async def get_next_log_id():
    try:
        last = await db["User_Interaction_Log"].find_one(sort=[("Interaction_Log_ID", -1)])
        return (last["Interaction_Log_ID"] + 1) if last else 1
    except PyMongoError as e:
        raise DatabaseConnectionError("Failed to fetch latest Interaction_Log_ID", extra={"error": str(e)})