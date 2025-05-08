from Config.database.DB_Config import  settlement_collection, case_settlement_collection, case_details_collection, request_log_collection
from datetime import datetime
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from pymongo.errors import PyMongoError

def update_db_status(db, request):
    try: 
        db[case_settlement_collection].update_one({"settlement_id": request.settlement_id}, {"$set": {"settlement_status": "Completed"}})
        db[settlement_collection].update_one({"settlement_id": request.settlement_id}, {"$set": {"status": "Completed"}})
        db[case_details_collection].update_one({"case_id": request.case_id}, {"$set": {"case_current_status": "Complete"}})
        # db[request_log_collection].update_one({"case_id": request.case_id}, {"$set": {"request_status": "Complete", "order_id": 3}})
        #call the request log API
        add_case_status = {
            "case_status": "Closed", 
            "status_reason": None,
            "created_dtm": datetime.now(),
            "created_by": "admin",
            "notified_dtm": datetime.now(),
            "expire_dtm": "2025-02-28T00:00:00.000+00:00"  # Adjust expiry date
        }
        db[case_details_collection].update_one(
            {"case_id": request.case_id},  # Filter by case_id
            {"$push": {"case_status": add_case_status}}
        )
        
    except PyMongoError as db_error:
        raise DatabaseError("Failed to update the database with the status.")        