from datetime import datetime
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from pymongo.errors import PyMongoError

case_settlement_collection = "Case_Settlements"
settlement_collection = "Settlements"
request_log_collection = "Request_Log"
case_details_collection ="Case_details"

def update_db_status(db, request):
    try: 
        db[case_settlement_collection].update_one({"settlement_id": request.settlement_id}, {"$set": {"settlement_status": "Completed"}})
        db[settlement_collection].update_one({"settlement_id": request.settlement_id}, {"$set": {"status": "Completed"}})
        db[case_details_collection].update_one({"case_id": request.case_id}, {"$set": {"case_current_status": "Complete"}})
        # db[request_log_collection].update_one({"case_id": request.case_id}, {"$set": {"request_status": "Complete", "order_id": 3}})
        #call the request log API
        expire_dtm = db[case_details_collection].find_one({"case_id": request.case_id})["case_status"][0]["expire_dtm"]
        add_case_status = {
            "case_status": "Closed", 
            "status_reason": "Settlement Completed",
            "created_dtm": datetime.now(),
            "created_by": "admin",
            "notified_dtm": datetime.now(),
            "expire_dtm": expire_dtm
        }
        db[case_details_collection].update_one(
            {"case_id": request.case_id},  # Filter by case_id
            {"$push": {"case_status": add_case_status}}
        )

    except PyMongoError as db_error:
        raise DatabaseError("Failed to update the database with the status.")        