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

from fastapi import APIRouter, HTTPException, BackgroundTasks
from http import HTTPStatus
from datetime import datetime, timezone, timedelta
import pytz  
from openApi.models.obtain_money_transaction_class import Money_Transaction_Model
from openApi.routes.existing_transaction import existing_case_transaction
from openApi.routes.new_case_transaction import new_case_transaction
from pydantic import ValidationError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError
from utils.logger import SingletonLogger
from utils.connectionMongo import MongoDBConnectionSingleton

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')
db_logger = SingletonLogger.get_logger('dbLogger')

case_details_collection ="Case_details"
case_settlement_collection = "Case_Settlements"
money_transactions_collection = "Money_Transactions"
money_transactions_rejected_collection = "Money_Transactions_Rejected"

def process_money_transaction(request):
    # Function to process the money transaction
    try:
        
        with MongoDBConnectionSingleton() as db:
            if db is None:
                db_logger.error("Failed to connect to MongoDB.")
                return False, "Failed to connect to MongoDB."

            db_logger.info(f"Connected to MongoDB database: {db.name}")
        
            start_time = datetime.now()
            try:
                unique_key = (f"{request.case_id}-{request.account_num}-{str(request.money_transaction_ref)}")
                # Setting attributes to determine the commission eligibility
                commission_eligible = True
                commission_type = "No Commission"
        
                created_dtm = datetime.now()
                #convert to dictionary < transaction_data_dict
                transaction_data_dict = request.model_dump()  #recieved_data_dic
                transaction_data_dict["created_dtm"] = created_dtm
                
                #Check if the case exists in the case details
                existing_case_details = db[case_details_collection].find_one({"case_id":request.case_id})
                logger.info("f"f"{unique_key} - Obtain Money Transaction - Case details found")
                if not existing_case_details:
                    logger.error(f"{unique_key} - Obtain Money Transaction - Case does not exist in the case details collection")
                    db[money_transactions_rejected_collection].insert_one(transaction_data_dict)   #add to rejected collection
                    raise ValidationError("Case does not exist in the case details collection - Invalid case_id")
                
                if existing_case_details["current_case_phase"] not in ["Negotiation", "Mediation Board"]:
                    logger.warning(f"{unique_key} - Obtain Money Transaction - Case phase is not in Negotiation or Mediation Board ")
                    commission_eligible = False
                    commission_type = "No Commission"
                
                # Check if the money_transaction_ref already exists in the money_transactions collection
                existing_money_transaction = db[money_transactions_collection].find_one({
                    "account_num": request.account_num,
                    "money_transaction_ref": request.money_transaction_ref
                })
                logger.info(f"{unique_key} - Obtain Money Transaction - Checking for existing money transaction")

                if existing_money_transaction:
                    logger.error(f"{unique_key} - Obtain Money Transaction - Money Transaction already exists")
                    db[money_transactions_rejected_collection].insert_one(transaction_data_dict)   #add to rejected collection
                    raise ValidationError("Money Transaction already EXISTS with money_transaction_ref or money_transaction_id")
                            
                #Get the case settlement by the settlement_id
                get_settlement = db[case_settlement_collection].find_one({"settlement_id": request.settlement_id})
                logger.info(f"{unique_key} - Obtain Money Transaction - Checking for existing settlement")
                
                if not get_settlement:
                    #No settlement found
                    logger.warning(f"{unique_key} - Obtain Money Transaction - Settlement plan NOT available")
                    drc_id = None
                    ro_id = None
                    commission_eligible = False
                    commission_type = "No Commission"
        
                else:
                    if get_settlement["settlement_status"] == "Completed":    
                        logger.info(f"{unique_key} - Settlement already completed payment accepting")
                    
                    if get_settlement["case_phase"] not in ["Negotiation", "Mediation Board"]:
                        logger.warning(f"{unique_key} - Obtain Money Transaction - Case phase is not in Negotiation or Mediation Board ")
                        commission_eligible = False
                        commission_type = "No Commission"
                    else:
                        drc_id = get_settlement["drc_id"]
                        ro_id = get_settlement["ro_id"]  
                    
                # Create new money_transaction_id -- Begin    
                last_transaction = db[money_transactions_collection].find_one(
                    {},
                    sort=[("money_transaction_id", -1)]
                )
                logger.info(f"{unique_key} - Obtain Money Transaction - Checking for last transaction")
                if last_transaction and "money_transaction_id" in last_transaction:
                    money_transaction_id = last_transaction["money_transaction_id"] + 1
                else:
                    money_transaction_id = 1
                # Create new money_transaction_id -- End      
                    
                #Check if the case_id exists in the money transaction collection
                money_transaction_details = db[money_transactions_collection].find_one(
                    {"case_id": request.case_id, "settlement_id": request.settlement_id},  
                    sort=[("created_dtm", DESCENDING)]  # Sort by latest created_dtm
                    )
                logger.info(f"{unique_key} - Obtain Money Transaction - Checking for existing money transaction details")
                
                if get_settlement and "settlement_plan" in get_settlement:
                        settlement_plan = get_settlement["settlement_plan"]
                logger.info(f"{unique_key} - Obtain Money Transaction - Settlement plan obtained")
                
                if money_transaction_details:
                    #case found
                    logger.info(f"{unique_key} - Obtain Money Transaction - Existing case found")
                    return existing_case_transaction(request, db, unique_key, money_transaction_details, settlement_plan, commission_eligible, created_dtm, transaction_data_dict, money_transaction_id, get_settlement, start_time, commission_type, drc_id, ro_id)
        
                #new case
                logger.info(f"{unique_key} - Obtain Money Transaction - New case found")
                return new_case_transaction(request, db, unique_key, start_time, created_dtm, commission_eligible, get_settlement, settlement_plan, transaction_data_dict, money_transaction_id, commission_type, drc_id, ro_id)

            except ValidationError as ve:
                logger.error(f"C-1P48 - Obtain Money Transaction - validation error: {ve}")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))
                
            except Exception as e:
                logger.error(f"C-1P48 - Obtain Money Transaction - Unexpected error: {e}")
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
    
    except PyMongoError as e:
        db_logger.error(f"C-1P48 - Obtain Money Transaction - Database error: {e}")
        raise DatabaseError("Database operation failed. Please try again later.")   