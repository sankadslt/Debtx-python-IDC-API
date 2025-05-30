"""
API : SET-2P01
Name : Create Settlement Plan
Description : Create a new settlement plan and add it to the database
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP :  settlement_id
      created_by
      created_on
      settlement_phase
      settlement_status
      status_dtm
      settlement_type
      settlement_amount
      last_monitoring_dtm
      settlement_plan_received[]
      settlement_plan[]
      settlement_occurred[]
      expire_date
      case_id
      ro_id
OP : None
*/
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: product_manager.py, product_manager_class.py, dateTimeValidator.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2024-02-17
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes: The logic for the settlement plan creation is implemented in the create_settlement_class.py file.
"""

from loggers.loggers import get_logger
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from dateutil.relativedelta import relativedelta 
from utils.database.connectDB import get_db_connection
from openApi.models.create_settlement_class import Create_Settlement_Model, settlement_model
# from config.database.DB_Config import case_settlement_collection, settlement_collection
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError

router = APIRouter()
logger = get_logger("Settlement_Manager")
db = get_db_connection()

case_settlement_collection = "Case_Settlements"
settlement_collection = "Settlements"
case_details_collection = "Case_details"

@router.post("/Create_Settlement_Plan", summary="Create a settlement plan", description = """**Mandatory Fields**<br>
- `created_by` <br>
- `case_phase` <br>
- `status_dtm` (MM/DD/YYYY HH24:MM:SS) <br>
- `settlement_type` <br>
- `settlement_amount` <br>
- `settlement_plan_received` <br>
- `case_id` <br>
- `remark` <br><br>

**Optional Fields:**<br>
- `ro_id` <br>
- `drc_id` <br>
- `status_reason` <br><br>


**Conditions:**<br>
1. If `settlement_type` is `"Type A"`, then `settlement_plan_received` should be a tuple **(initial amount, total months)**.  
2. If `settlement_type` is `"Type B"`, then `settlement_plan_received` should be a tuple **(initial amount, list of installment amounts)**.  
"""
)
async def create_settlement_plan(request:Create_Settlement_Model):
    logger.info("SET-2P01 - Create Settlement Plan - Details recieved")
    
    try:
        #Check if the settlement ID already exists in the database
        logger.info("SET-2P01 - Create Settlement Plan - Checking if the case ID exists in the database")
        existing_case = db[case_details_collection].find_one({"case_id": request.case_id})
        
        #region Add the details to the database
        if not existing_case:
            #If the settlement ID already exists, raise an error
            logger.error(f"SET-2P01 - Create Settlement Plan - Case ID {request.case_id} does not exist in the database.")           
            ValidationError(f"SET-2P01 - Create Settlement Plan - Case ID {request.case_id} does not exist. Invalid case ID.") 
            return HTTPException(
                status_code=HTTPStatus.CONFLICT, detail=f"SET-2P01 - Create Settlement Plan - Case ID {request.case_id} does not exist. Invalid case ID."
            )
        
        #Create new settlement ID
        logger.info("SET-2P01 - Create Settlement Plan - Creating new settlement ID")
        latest_settlement = db[case_settlement_collection].find_one(
            {"settlement_id": {"$exists": True}}, sort=[("settlement_id", -1)]
        )
        if latest_settlement:
            new_settlement_id = latest_settlement["settlement_id"] + 1
        else:
            new_settlement_id = 1
        
        request.settlement_id = new_settlement_id
        logger.info(f"SET-2P01 - Create Settlement Plan - New settlement ID created: {request.settlement_id}")    
        
        #assign expire date 
        expire_dtm = request.created_on + relativedelta(months=12)
        request.expire_date = expire_dtm
        request.last_monitoring_dtm = request.created_on
            
        try:                        
            #Add the details to the settlement plan database
            db[case_settlement_collection].insert_one(request.model_dump())
            logger.info("SET-2P01 - Create Settlement Plan - Details added successfully to case settlement plan db")
            
            created_dtm = request.created_on
            #Add the details to the settlement database
            settlement_model_db = settlement_model(
                settlement_id = new_settlement_id,
                settlement_created_dtm = created_dtm,
                status = request.settlement_status,
                drc_id = request.drc_id,
                ro_id = request.ro_id
            )
            db[settlement_collection].insert_one(settlement_model_db.model_dump())
            
            return {"message": "Create Settlement Plan - Details added successfully to case settlement plan db"}
        
        except PyMongoError as pe:
            logger.error(f"SET-2P01 - Create Settlement Plan - PyMongo error: {pe}")
            raise DatabaseError(f"SET-2P01 - Create Settlement Plan - PyMongo error: {pe}")    
    #endregion            
    
    except ValidationError as ve:
        logger.error(f"SET-2P01 - Create Settlement plan - validation error: {ve}")
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))
        
    except Exception as e:
        logger.error(f"SET-2P01 - Create Settlement plan - Unexpected error: {e}") 
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")           