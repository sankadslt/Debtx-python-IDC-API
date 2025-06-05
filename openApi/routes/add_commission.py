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
case_details_collection = "Case_details"
caterlogue_collection = "Commission_Caterlogue"
payment_rate_collection = "Commission_Payment_Rate"
cpe_rate_collection = "Commission_CPE_Rate"


def add_to_commission(db,unique_key, case_id, money_transaction_id, commission_type, commissioning_amount, drc_id, ro_id):
    try:
        logger.info(f"{unique_key} - Starting commission addition process.")

        commission_action = "payment"
        logger.info(f"{unique_key} - Commission action set to: {commission_action}")

        matched_caterlogue = db[caterlogue_collection].find_one(
            {"commission_action": commission_action},
            sort=[("caterlog_id", DESCENDING)])
        logger.info(f"{unique_key} - Matching catalogue entries for action: {matched_caterlogue}")
        
        # matched_caterlogue = list(matched_caterlogue)
        # logger.info(f"{unique_key} - Matched catalogue entries: {matched_caterlogue}")
        if not matched_caterlogue:
            raise DatabaseError(f"No matching catalogue entry found for action: {commission_action}")
        
        caterlog_id = matched_caterlogue["caterlog_id"]
        logger.info(f"{unique_key} - Found caterlog_id: {caterlog_id} for action: {commission_action}")


        if commission_action == "payment":
            max_rate_entry = db[payment_rate_collection].find_one(
                {"caterlog_id": caterlog_id},
                sort=[("commission_payment_rate_id", DESCENDING)]
            )
            commission_payment_rate_id = max_rate_entry["commission_payment_rate_id"]
            logger.info(f"{unique_key} - Commission payment rate ID: {commission_payment_rate_id}")
        
        # elif commission_action == "cpe":
        #     max_rate_entry = db[cpe_rate_collection].find_one(
        #         {"caterlog_id": caterlog_id},
        #     sort=[("commission_cpe_rate_id", DESCENDING)]
        #     )
        #     commission_cpe_rate_id = max_rate_entry["commission_cpe_rate_id"]
        #     logger.info(f"{unique_key} - Commission CPE rate ID: {commission_cpe_rate_id}")

        else:
            raise DatabaseError(f"Unsupported commission action: {commission_action}")

        if not max_rate_entry or "commission_rate" not in max_rate_entry:
            raise DatabaseError(f"Commission rate not found for catalog_id: {caterlog_id}")

        commission_rates = max_rate_entry["commission_rate"]
        logger.info(f"{unique_key} - Commission rates: {commission_rates}")


        # commission_rates = {"PEO TV": 10 / 100, "LTE": 10 / 100, "Fiber": 10 / 100}
        
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
            commission_action = "payment",
            caterlog_id= caterlog_id,
            commission_payment_rate_id= commission_payment_rate_id,
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