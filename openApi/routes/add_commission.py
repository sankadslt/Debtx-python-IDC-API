"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions - add commissions (Check RO-Negotiation, Settlement Plan)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : 
        
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

from openApi.models.commission_model_class import Commission_Model
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError
from datetime import datetime
from pymongo import DESCENDING
from utils.logger import SingletonLogger

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')
db_logger = SingletonLogger.get_logger('dbLogger')

commission_collection = "Commission"
case_details_collection ="Case_details"


def add_to_commission(db,unique_key, case_id, money_transaction_id, commission_type, commissioning_amount, drc_id, ro_id):
    try:
        commission_rates = {"PEO TV": 10 / 100, "LTE": 10 / 100, "Fiber": 10 / 100}
        
        logger.info(f"{unique_key} - Adding commission to the database.")
        existing_case_details = db[case_details_collection].find_one({"case_id": case_id})
        drc_commission_rule = existing_case_details["drc_commision_rule"]    
        commission_amount = commissioning_amount * commission_rates.get(drc_commission_rule, 0)
        highest_commission_seq = db[commission_collection].find_one(
        {},  # No filter, fetch any document
        sort=[("commission_seq", DESCENDING)]  # Sort by bonus_seq in descending order
        )
        commission_seq = highest_commission_seq["commission_seq"] if highest_commission_seq else 0
        
        commission_data = Commission_Model(
            commission_seq = commission_seq + 1,
            created_dtm = datetime.now(),
            commission_action = "Payment",
            catalog_id=0,
            commission_pay_rate_id=0,
            commission_ref = drc_commission_rule,
            transaction_ref =  money_transaction_id,
            case_id = case_id,
            drc_id = drc_id,
            ro_id = ro_id,
            commission_amount = commission_amount,
            commission_type = commission_type,
            commission_status = "Pending",
            commission_status_on = datetime.now(),
            commission_status_reason=None,
            checked_by=None,
            checked_on=None,
            approved_on=None,
            approved_by=None
        )

        db[commission_collection].insert_one(commission_data.model_dump())
        logger.info(f"{unique_key} - Commission added successfully.")
        
    except PyMongoError as db_error:
        db_logger.error(f"{unique_key} - Database error during update: {str(db_error)}")
        raise DatabaseError("Failed to update the database with commission.")