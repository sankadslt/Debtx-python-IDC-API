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
from datetime import datetime, timedelta
import calendar    
from utils.database.connectDB import get_db_connection
from openApi.models.create_settlement_class import Create_Settlement_Model, settlement_model
# from config.database.DB_Config import case_settlement_collection, settlement_collection
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError, NotFoundError

router = APIRouter()
logger = get_logger("Settlement_Manager")
db = get_db_connection()

case_settlement_collection = "Case_Settlements"
settlement_collection = "Settlements"

@router.post("/Create_Settlement_Plan", summary="Create a settlement plan", description = """**Mandatory Fields**<br>
- `settlement_id` <br>
- `created_by` <br>
- `created_on` (MM/DD/YYYY HH24:MM:SS) <br>
- `settlement_phase` <br>
- `settlement_status` <br>
- `status_dtm` (MM/DD/YYYY HH24:MM:SS) <br>
- `settlement_type` <br>
- `settlement_amount` <br>
- `last_monitoring_dtm` (MM/DD/YYYY HH24:MM:SS) <br>
- `settlement_plan_received` <br>
- `settlement_plan` (array) <br>
- `settlement_occurred` (array) <br>
- `expire_date` (MM/DD/YYYY HH24:MM:SS) <br>
- `case_id` <br>
- `ro_id` <br><br>

**Optional Fields:**<br>
- `drc_id` <br>
- `status_reason` <br>
- `remark` <br><br>

**Valid settlement_status values:**<br>
- "Open" 
- "Open_Pending"  
- "Active" 
- "Withdraw"
- "Completed"  <br><br>

**Conditions:**<br>
1. If `settlement_type` is `"Type A"`, then `settlement_plan_received` should be a tuple **(initial amount, total months)**.  
2. If `settlement_type` is `"Type B"`, then `settlement_plan_received` should be a tuple **(initial amount, list of installment amounts)**.  
3. Each `settlement_plan` entry must contain **`installment_seq`, `installment_settle_amount`, and `plan_date`**.  
4. Each `settlement_occurred` entry must contain **`installment_seq`, `installment_settle_amount`, `plan_date`, `payment_seq`, and `installment_paid_amount`**.  
"""
)
async def create_settlement_plan(request:Create_Settlement_Model):
    logger.info("SET-2P01 - Create Settlement Plan - Details recieved")
    
    try:
        #Check if the settlement ID already exists in the database
        logger.info("SET-2P01 - Create Settlement Plan - Checking if the request ID already exists in the database")
        existing_settlement_plan = db[case_settlement_collection].find_one({"settlement_id": request.settlement_id})
        
        #region Add the details to the database
        if existing_settlement_plan:
            #If the settlement ID already exists, raise an error
            logger.error(f"SET-2P01 - Create Settlement Plan - Settlement ID {request.settlement_id} already exists in the database.")           
            ValidationError(f"SET-2P01 - Create Settlement Plan - Settlement ID {request.settlement_id} already exists.") 
            return HTTPException(
                status_code=HTTPStatus.CONFLICT, detail=f"SET-2P01 - Create Settlement Plan - Settlement ID {request.settlement_id} already exists."
            )
            
        else:
            try:                            
                #Add the details to the settlement plan database
                db[case_settlement_collection].insert_one(request.model_dump())
                logger.info("SET-2P01 - Create Settlement Plan - Details added successfully to case settlement plan db")
                
                #Add the details to the settlement database
                settlement_model_db = settlement_model(
                    settlement_id = request.settlement_id,
                    settlement_created_dtm = request.created_on,
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