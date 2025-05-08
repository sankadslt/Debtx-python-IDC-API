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

from Config.database.DB_Config import drc_bonus_collection ,money_transactions_collection
from utils.database.connectDB import get_db_connection
from openApi.models.obtain_money_transaction_class import DRC_Bonus
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from loggers.loggers import get_logger

db = get_db_connection()
logger = get_logger("Money_Manager")

def add_to_drc_bonus(money_transaction_type,commission_type, created_dtm, settlement_id, case_id, ro_id, commissioned_amount, agent_month, money_transaction_id, completion, money_transaction_amount):
    try:
        first_settlement_complete = False
        highest_bonus = db[drc_bonus_collection].find_one(
        {},  # No filter, fetch any document
        sort=[("bonus_seq", DESCENDING)]  # Sort by bonus_seq in descending order
        )
        highest_bonus_seq = highest_bonus["bonus_seq"] if highest_bonus else 0
        
        latest_valid_transaction = db[money_transactions_collection].find_one(
            {   "case_id": case_id,
                "settlement_id": settlement_id,
                "money_transaction_type": {"$nin": ["Bill", "Return Cheque"]}  # Exclude Bill & Return Cheque
            }, sort=[("created_dtm", DESCENDING)]  # Get the most recent valid transaction
        )

        # if not latest_commissioned_transaction and commission_type == "Commissioned":
        if (latest_valid_transaction["installment_seq"] == 1 and commission_type == "Commissioned") or completion:
            if money_transaction_type in ["Adjustment","Dispute","Cash","Cheque"]:
                first_settlement_complete = True if not completion else False
                drc_bonus_data = DRC_Bonus(
                    bonus_seq = highest_bonus_seq + 1,
                    created_dtm = created_dtm, 
                    case_id = case_id,
                    billing_center = ro_id,
                    commissioning_amount = commissioned_amount,
                    agent_month = agent_month,
                    bonus_type= "success rate" if not completion else "completion rate",
                    money_transaction_id = money_transaction_id,
                    bonus_status= True,
                    bonus_status_on= created_dtm,
                )
                db[drc_bonus_collection].insert_one(drc_bonus_data.model_dump())
            
        if money_transaction_type == "Return Cheque":
            logger.info(f"C-IP48 - Obtain Money Transaction - Return Cheque transaction detected for case_id: {case_id}. Updating bonus status")
            drc_bonus_data = DRC_Bonus(
                    bonus_seq = highest_bonus_seq + 1,
                    created_dtm = created_dtm, 
                    case_id = case_id,
                    billing_center = ro_id,
                    commissioning_amount = commissioned_amount,
                    agent_month = agent_month,
                    bonus_type= "success rate" if not completion else "completion rate",
                    money_transaction_id = money_transaction_id,
                    bonus_status= False,
                    bonus_status_on= created_dtm,
                )
            db[drc_bonus_collection].insert_one(drc_bonus_data.model_dump())
        return first_settlement_complete    
                      
    except PyMongoError as db_error:
        logger.error(f"C-1P48 - Database error during update: {str(db_error)}")
        raise DatabaseError("Failed to update the database with bonus.")    