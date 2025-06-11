#region-Details_Template
"""
API : CPY-1P03
Name :           Case Distribution To DRC
Description :    Approved case distrbution to DRC
Created By :     Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
Created No :

Version: 1.0
Input_parameter :  case_id , Created_By(optional-default system_user)
Output:           *Status Changes,Updating drc & approve arrays , Inserting Documents
Operation :       *Update case status to 'open with agent'
                  *add DRC
                  *insert approval details
                  *register drc Monitor 
     
Collections:      *Case_details-                        -Write
                  *tmp_forwarded_approver               -Read
                  *Temp_Case_Distribution_DRC_Details   -Read & write
                  *Case_Monitor_log                     -Write 
                  *Case_Monitor                         -Write
                  
                  

*/    
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: approved case distribution to DRC
    Version:
        version: 1.0
        Last Modified Date: 2024-04-02
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template

from datetime import datetime
from fastapi import FastAPI, Query
from pymongo.errors import PyMongoError
import requests
from dateutil.relativedelta import relativedelta
from utils.get_last_day_of_month.get_last_day_of_month import get_last_day_of_month
from pymongo import MongoClient
from utils.custom_exceptions.cust_exceptions import CaseIdNotFoundError, DataFetchError, DocumentUpdateError , DatabaseConnectionError, BaseCustomException ,ValidationError
from utils.config_loader_db import config
from utils.db import db ,mongo_client
from utils.logger.loggers import SingletonLogger
from utils.connectAPI import Get_API_URL_Singleton

SingletonLogger.configure() 

logger = SingletonLogger.get_logger('dblogger')



def process_case_distribution_to_drc(case_id: int, Created_By: str):
    """
    Processes the case approval for distribution to DRC using MongoDB transactions.
    """
    logger.debug(f"Processing case distribution to DRC for case_id: {case_id}")
    
    session = None
    
    try:

        logger.debug("Connected to MongoDB db Successfully")
        
        session = mongo_client.client.start_session()
        
        with session.start_transaction():
             #region- Fetching data from collections begin
             
            case_details_collection = db.Case_details
            case_document = case_details_collection.find_one({"case_id": case_id}, session=session)
            if not case_document:
                raise CaseIdNotFoundError(f"Case ID {case_id} not found")
            
            # Retrieve case distribution batch ID
            case_distribution_batch_id = case_document.get("case_distribution_batch_id")
            if not case_distribution_batch_id:
                raise DataFetchError(f"case_distribution_batch_id not found for case details {case_id}")
            
              # Fetch approver details
            approver_collection = db.Template_forwarded_approver
            approver_document = approver_collection.find_one({"approver_reference": case_distribution_batch_id}, session=session)
            
            # Fetch DRC details
            drc_collection = db.Template_case_distribution_drc_details
            drc_document = drc_collection.find_one({"case_id": case_id}, session=session)

            if not drc_document:
                raise DataFetchError("DRC details not found for the given Case ID")
            
            
            # Retrieve DRC ID from the document
            drc_id = drc_document.get("new_drc_id") or drc_document.get("drc_id")
            
             # Update 'proceed_on' field in the DRC collection
            drc_collection.update_one(
                {"case_id": case_id},
                {"$set": {"proceed_on": datetime.utcnow()}},
                session=session
            )
            
            logger.info(f"Proceed on updated for case ID {case_id}")
            
            # Extract remark from the approver document if available
            remark_list = approver_document.get("remark", []) if approver_document else []
            remark_value = remark_list[0].get("remark") if remark_list else None
            #endregion-fetching data from collections end
             
            # Prepare update data for the case 
            update_data = {
                "$set": {"case_current_status": "Open With Agent"},
                "$push": {
                    "case_status": {"case_status": "Open With Agent"},
                    "drc": {
                        "DRC_status": "Open With Agent",
                        "Created_dtm": datetime.utcnow(),
                        "status_dtm": datetime.utcnow(),
                        "drc_id": drc_id,
                    },
                    "approve": {
                        "Approval_type": "DRC_Distribution",
                        "Approved_by": approver_document.get("approved_deligated_by") if approver_document else None,
                        "Approved_on": approver_document.get("created_on") if approver_document else None,
                        "remark": remark_value,
                    }
                }
            }
            # Update case details
            case_update_result = case_details_collection.update_one({"case_id": case_id}, update_data, session=session)
            if case_update_result.modified_count == 0:
                raise DocumentUpdateError("Error updating case details")
            
            logger.info(f"Case details updated for case_id: {case_id}")
            
              # API Call Handling to fetch case phase
            try:
                api_url_singleton = Get_API_URL_Singleton()
                api_url = api_url_singleton.get_api_url()
                
                if not api_url:
                    logger.error("API URL could not be resolved from configuration")
                    raise ValidationError("API URL is missing or invalid in configuration")

                response = requests.get(api_url, params={"case_status": "Open With Agent"},timeout=10)
                
                 # Raise an exception for HTTP errors (e.g., 4xx or 5xx)
                response.raise_for_status()
                try:
                     # Attempt to parse the JSON response
                    response_json = response.json()
                    # Extract the 'case_phase' from the response JSON
                    case_phase = response_json.get("case_phase")
                    
                     # Check if 'case_phase' is missing or invalid
                    if not case_phase or case_phase == "Unknown":
                        logger.error(f"Invalid or missing case_phase for case_id{case_id}")
                        raise ValidationError("case_phase could not be determined from the API response")
                except ValueError as e:
                    logger.error(f"Invalid JSON response:{str(e)}")
                    raise ValidationError("Invalid response format while retrieving case_phase")
                    
            except requests.Timeout:
                logger.error("Request timed out")
                raise ValidationError(f"Request timed out while fetching case phase:{str(e)}")
                     
            except requests.RequestException as e:
                logger.error(f"Failed to fetch case phase: {str(e)}")
                raise ValidationError("Failed to fetch case phase from API")
                

            logger.debug(f"Case Phase fetched for case ID {case_id}: {case_phase}")
            
            
            # Determine case monitoring expiration date (3 months ahead)
            created_dtm = datetime.utcnow()
            monitor_expir_dtm = get_last_day_of_month(created_dtm + relativedelta(months=3))
            
             #region- Insert record into Case_Monitor_Log & Case_Monitor begin
            case_monitor_log_collection = db.Case_Monitor_Log
            case_monitor_log_collection.insert_one({
                "doc_version":1.0,
                "case_id": case_id,
                "Created_dtm": created_dtm,
                "Case_Phase": case_phase, 
                "Monitor_Expir_Dtm": monitor_expir_dtm,
                "Last_Monitor_Dtm": datetime.utcnow(),
            }, session=session)
            
            logger.info(f"Case monitor log inserted for case_id: {case_id}")
            
            # Insert record into Case_Monitor
            case_monitor_collection = db.Case_Monitor
            case_monitor_collection.insert_one({
                "doc_version":1.0,
                "case_id": case_id,
                "Created_dtm": created_dtm,
                "Created_By": Created_By,
                "Case_Phase": case_phase, 
                "Monitor_Expir_Dtm": monitor_expir_dtm,
                "Last_Monitor_Dtm": datetime.utcnow(), 
                "Last_Requested_On": None
            }, session=session)
            #endregion
            logger.info(f"Case monitor record inserted for case_id: {case_id}")
            
            # Commit transaction if everything is successful
            session.commit_transaction()
            
            return (f"Case updated and Monitor records inserted successfully for case_id: {case_id}")

    except BaseCustomException as e:
        logger.error(f"Custom Exception: {str(e)}")
        if session and session.in_transaction:
            session.abort_transaction()
        raise 
    
    except PyMongoError as e:
        logger.error(f"Database Error: {str(e)}")
        if session and session.in_transaction:
            session.abort_transaction()
        raise DatabaseConnectionError("Database operation failed") 

    except Exception as e:
        logger.error(f"Unexpected error [{type(e).__name__}]: {str(e)}")
        if session and session.in_transaction:
            session.abort_transaction()
        raise 
    

