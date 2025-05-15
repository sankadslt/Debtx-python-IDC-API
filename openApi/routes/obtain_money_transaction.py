"""
API :  C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By :  Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : 
      case_id
      account_num
      settlement_id
      money_transaction_type  
      money_transaction_ref
      money_transaction_amount
      money_transaction_date
      bill_payment_status
      case_phase
      drc_id
      ro_id
        
OP : None
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: obtain_money_transaction.py, obtain_money_transaction_class.py, add_drc_bonus.py, 
                   update_db_status.py, manage_cheque_payment_for_completing_settlement.py, 
                   money_transaction_type.py, add_commission.py
    Purpose:    
    Version:
        version: 1.0
        Last Modified Date: 2025-03-23
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""
from loggers.loggers import get_logger
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from datetime import datetime, timezone, timedelta
import pytz  
from utils.database.connectDB import get_db_connection
from openApi.models.obtain_money_transaction_class import Money_Transaction_Model
from Config.database.DB_Config import money_transactions_collection, settlement_collection, ro_negotiation_collection, case_settlement_collection, case_details_collection, money_transactions_rejected_collection
from openApi.routes.existing_transaction import existing_case_transaction
from openApi.routes.new_case_transaction import new_case_transaction
from pydantic import ValidationError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError

router = APIRouter()
logger = get_logger("Money_Manager")
db = get_db_connection()

@router.post("/Obtain_Money_Transaction", summary="Get all the money related transactions", description = """**Mandatory Fields**<br>
- `money_transaction_id` <br>
- `case_id` <br>
- `settlement_id` <br>
- `money_transaction_type` <br>
- `money_transaction_ref` <br>
- `money_transaction_amount` <br>
- `money_transaction_date` (MM/DD/YYYY HH24:MM:SS) <br>
- `bill_payment_status` <br>
- `case_phase` <br>
- `drc_id` <br>
- `ro_id` <br><br>

**Valid money_transaction_type values:** - "Bill","Adjustment","Dispute","Cash","Cheque","Return Cheque"  <br><br>
**Valid case_phase values:** - "Negotiation", "Mediation Board", "LOD", "Litigation", "WRIT" <br><br>
""")
async def obtain_money_transaction(request:Money_Transaction_Model):
    logger.info("C-1P48 - Obtain Money Transaction - Request received")
    start_time = datetime.now()
    try:
        # Checking for the settlement phase to determine the commission eligibility
        commission_eligible = True
        commission_type = "No Commission"
 
        # checking if the money_transaction_ref already exists in the db
        # Check account_num related transactions
        related_transactions = list(db[money_transactions_collection].find({
            "account_num": request.account_num
        }))

        # Check if any of them has the same money_transaction_ref
        existing_money_transaction = next(
            (tx for tx in related_transactions if tx["money_transaction_ref"] == request.money_transaction_ref),
            None
        )
        created_dtm = datetime.now()
        transaction_data = request.model_dump()  
        transaction_data["created_dtm"] = created_dtm
        if existing_money_transaction:
            logger.error(f"C-1P48 - Obtain Money Transaction - Money Transaction already exists")
            db[money_transactions_rejected_collection].insert_one(transaction_data)   #add to rejected collection
            raise ValidationError("Money Transaction already EXISTS with money_transaction_ref or money_transaction_id")
        
        #Check if the case exists in the case details
        existing_case_details = db[case_details_collection].find_one({"case_id":request.case_id})
        if not existing_case_details:
            logger.error(f"C-1P48 - Obtain Money Transaction - Case does not exist in the case details collection")
            db[money_transactions_rejected_collection].insert_one(transaction_data)   #add to rejected collection
            raise ValidationError("Case does not exist in the case details collection - Invalid case_id")               
        
        if request.case_phase not in ["Negotiation", "Mediation Board"]:
            commission_eligible = False
            commission_type = "No Commission"
        
        #Get the case settlement by the settlement_id
        get_settlement = db[case_settlement_collection].find_one({"settlement_id": request.settlement_id})
        if get_settlement["settlement_status"] == "Completed":    
            logger.info(f"Settlement already completed payment accepting")

        if not get_settlement:
            logger.info(f"C-1P48 - Obtain Money Transaction - Settlement plan NOT available")
        
        if get_settlement["settlement_phase"] not in ["Negotiation", "Mediation Board"]:
            logger.info(f"C-1P48 - Obtain Money Transaction - Settlement phase is not in Negotiation or Mediation Board")
            commission_eligible = False
        
        last_transaction = db[money_transactions_collection].find_one(
            {},
            sort=[("money_transaction_id", -1)]
        )
        if last_transaction and "money_transaction_id" in last_transaction:
            money_transaction_id = last_transaction["money_transaction_id"] + 1
        else:
            money_transaction_id = 1
            
        #Check if the case_id exists in the money transaction collection
        existing_case = db[money_transactions_collection].find_one(
            {"case_id": request.case_id, "settlement_id": request.settlement_id},  
            sort=[("created_dtm", DESCENDING)]  # Sort by latest created_dtm
            )
        
        if get_settlement and "settlement_plan" in get_settlement:
                existing_settlement_plan = get_settlement["settlement_plan"]
        
        if existing_case:
            #case found
            return existing_case_transaction(request, db, existing_case, existing_settlement_plan, commission_eligible, created_dtm, transaction_data, money_transaction_id, get_settlement, start_time, commission_type )
        
        else: 
            #new case
            return new_case_transaction(request, db, start_time, created_dtm, commission_eligible, get_settlement, existing_settlement_plan, transaction_data, money_transaction_id, commission_type)

    except ValidationError as ve:
        logger.error(f"C-1P48 - Obtain Money Transaction - validation error: {ve}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))
        
    except Exception as e:
        logger.error(f"C-1P48 - Obtain Money Transaction - Unexpected error: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")        