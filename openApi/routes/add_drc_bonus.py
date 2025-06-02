"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : money_transaction_type, created_dtm, case_id, ro_id, commissioned_amount, agent_month, money_transaction_id, completion, money_transaction_amount
        
OP : None
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: obtain_money_transaction.py, obtain_money_transaction_class.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2025-03-23
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

from openApi.models.obtain_money_transaction_class import DRC_Bonus
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from utils.logger import SingletonLogger

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')
db_logger = SingletonLogger.get_logger('dbLogger')

drc_bonus_collection = "DRC_Bonus"
money_transactions_collection = "money_transactions"


def add_to_drc_bonus(db, unique_key, money_transaction_type,commission_type, created_dtm, settlement_id, case_id, ro_id, commissioned_amount, agent_month, money_transaction_id, completion, money_transaction_amount):
    try:
        first_settlement_complete = False
        year_month_format = int(created_dtm.strftime("%Y%m"))  
        highest_bonus = db[drc_bonus_collection].find_one(
        {},  # No filter, fetch any document
        sort=[("bonus_seq", DESCENDING)]  # Sort by bonus_seq in descending order
        )
        highest_bonus_seq = highest_bonus["bonus_seq"] if highest_bonus else 0
        
        latest_valid_transaction = db[money_transactions_collection].find_one(
            {   "case_id": case_id,
                "settlement_id": settlement_id,
                "money_transaction_type": {"$nin": ["Bill"]}  # Exclude Bill 
            }, sort=[("created_dtm", DESCENDING)]  # Get the most recent valid transaction
        )

        # if not latest_commissioned_transaction and commission_type == "Commissioned":
        if (latest_valid_transaction["installment_seq"] == 1 and commission_type == "Commissioned") or completion:
            if money_transaction_type in ["Adjustment","Dispute","Cash","Cheque"]:
                if not completion:
                    first_settlement_complete = True
                drc_bonus_data = DRC_Bonus(
                    bonus_seq = highest_bonus_seq + 1,
                    created_dtm = created_dtm, 
                    case_id = case_id,
                    billing_center = ro_id,
                    commissioning_amount = commissioned_amount,
                    agent_month = year_month_format,
                    bonus_type= "success rate" if not completion else "completion rate",
                    money_transaction_id = money_transaction_id,
                    bonus_status= True,
                    bonus_status_on= created_dtm,
                )
                db[drc_bonus_collection].insert_one(drc_bonus_data.model_dump())
                logger.info(f"{unique_key} - Obtain Money Transaction - Bonus added to DRC_Bonus collection") 
            
        if money_transaction_type == "Return Cheque" and commission_type == "Unresolved Commission" and latest_valid_transaction["installment_seq"] == 1: 
            logger.info(f"{unique_key} - Obtain Money Transaction - Return Cheque transaction detected for case_id: {case_id}. Updating bonus status")
            drc_bonus_data = DRC_Bonus(
                    bonus_seq = highest_bonus_seq + 1,
                    created_dtm = created_dtm, 
                    case_id = case_id,
                    billing_center = ro_id,
                    commissioning_amount = -commissioned_amount,
                    agent_month = year_month_format,
                    bonus_type= "success rate" if not completion else "completion rate",
                    money_transaction_id = money_transaction_id,
                    bonus_status= False,
                    bonus_status_on= created_dtm,
                )
            db[drc_bonus_collection].insert_one(drc_bonus_data.model_dump())
            logger.info(f"{unique_key} - Obtain Money Transaction - Bonus added to DRC_Bonus collection")
        return first_settlement_complete    
                      
    except PyMongoError as db_error:
        db_logger.error(f"{unique_key} - Database error during update: {str(db_error)}")
        raise DatabaseError("Failed to update the database with bonus.")    