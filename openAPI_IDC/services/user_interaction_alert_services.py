#region-Details_Template
"""
API : 
Name :               create_user_interaction_alert
Description :        creating an alert for user interaction
Created By :         Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
Created No :

Version: 1.0
Input_parameter :     Interaction_ID:int,
                      User_Interaction_Type: str,
                      delegate_user_id: int,
                      Created_By: str,
                      parameter_array: list[Any]

Input:               *Interaction_ID:int , Template_User_Interaction document

Output:              *inserting User_Interaction_Log document and inserting User_Interaction_progress_Log document

Operation :          *Read Template_User_Interaction document
                     *insert User_Interaction_Log document
                     *insert User_Interaction_progress_Log document
     
Collections:         *Template_User_Interaction            -Read
                     *User_Interaction_Log                 -Write
                     *User_Interaction_progress_Log        -Write

                  
                  

*/    
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: Alerting  user interaction
    Version:
        version: 1.0
        Last Modified Date: 2024-05-20
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template

from datetime import datetime
from fastapi import FastAPI
from pymongo.errors import PyMongoError
from pymongo import MongoClient
from utils.custom_exceptions.custom_exceptions import DocumentNotFoundError, DatabaseConnectionError, BaseCustomException , DataInsertError,InvalidInteractionIDError
from utils.config_loader import config
from typing import Any
from utils.db import db 
from utils.logger.loggers import SingletonLogger
from utils.get_next_log_id.get_next_log_id import get_next_log_id

db_logger = SingletonLogger.get_logger('dbLogger')


async def send_an_alert(
    Interaction_ID: int,
    User_Interaction_Type: str,
    delegate_user_id: int,
    Created_By: str,
    parameter_array:   list[Any]
):
    try:
        db_logger.debug(f"Received request to process Interaction_ID: {Interaction_ID}")

        if Interaction_ID not in config.interaction_id_numbers:
            db_logger.error(f"Interaction_ID {Interaction_ID} is not in allowed config list.")
            raise InvalidInteractionIDError(f"Interaction_ID {Interaction_ID} is not permitted.")

        log_id = await get_next_log_id()
        now = datetime.utcnow()

        # Fetch the Template_User_Interaction document
        template_user_interaction_document = await db["Template_User_Interaction_x"].find_one({"Interaction_ID": Interaction_ID})
        if not template_user_interaction_document:
            db_logger.error(f"No Template_User_Interaction found for Interaction_ID: {Interaction_ID}")
            raise DocumentNotFoundError("Template_User_Interaction not found.")

        expected_parameters = template_user_interaction_document.get("parameters", [])

        # Check parameter compatibility based on length only if failed insert log record with status "Error" and a reason
        if len(parameter_array) != len(expected_parameters):
            
            interaction_log_record = {
                "Interaction_Log_ID": log_id,
                "Interaction_ID": Interaction_ID,
                "User_Interaction_Type": User_Interaction_Type,
                "CreateDTM": now,
                "delegate_user_id": delegate_user_id,
                "Created_By": Created_By,
                "Interation_Mode": None,
                "User_Transaction_Status": "Error",
                "Parameters": parameter_array,
                "Transaction_Status_DTM": now,
                "Transaction_Status_Reason": "Parameters not compatible",
                "ToDo_On": None,
            }

            try:
                await db["User_Interaction_Log"].insert_one(interaction_log_record)
                db_logger.info(f"Inserted error log for incompatible parameters. Log ID: {log_id}")
            except PyMongoError as e:
                db_logger.error(f"Failed to insert error log: {str(e)}")
                raise DataInsertError("Failed to insert error log", extra={"error": str(e)})

            return {"message": "Alert logged with parameter mismatch", "Interaction_Log_ID": log_id}

        # Prepare success logs
        interaction_log_record = {
            "Interaction_Log_ID": log_id,
            "Interaction_ID": Interaction_ID,
            "User_Interaction_Type": User_Interaction_Type,
            "CreateDTM": now,
            "delegate_user_id": delegate_user_id,
            "Created_By": Created_By,
            "Interation_Mode": template_user_interaction_document.get("Interation_Mode"),
            "User_Transaction_Status": "Open",
            "Parameters": parameter_array,
            "Transaction_Status_DTM": now,
            "Transaction_Status_Reason": "Successful",
            "ToDo_On": template_user_interaction_document.get("ToDo_On"),
            "ToDo_ID": template_user_interaction_document.get("ToDoID"),
        }

        progress_log_record = {
            "Interaction_Log_ID": log_id,
            "Interaction_ID": Interaction_ID,
            "User_Interaction_Type": User_Interaction_Type,
            "CreateDTM": now,
            "delegate_user_id": delegate_user_id,
            "Interation_Mode": template_user_interaction_document.get("Interation_Mode"),
            "Created_By": Created_By,
            "User_Transaction_Status": "Open",
            "Parameters": parameter_array,
            "Transaction_Status_DTM": now,
            "ToDo_On": template_user_interaction_document.get("ToDo_On"),
            "Todo_ID": template_user_interaction_document.get("ToDoID"),
        }

        try:
            await db["User_Interaction_Log"].insert_one(interaction_log_record)
            await db["User_Interaction_progress_Log"].insert_one(progress_log_record)
            db_logger.debug(f"Inserted logs for successful interaction. Log ID: {log_id}")
        except PyMongoError as e:
            db_logger.error(f"Failed to insert logs: {str(e)}")
            raise DataInsertError("Failed to insert success logs", extra={"error": str(e)})

        return {"message": "Alert created successfully", "Interaction_Log_ID": log_id}

    except BaseCustomException as ce:
        db_logger.error(f"Custom exception: {str(ce)}")
        raise
    except Exception as e:
        db_logger.exception("Unexpected server error during alert creation")
        raise DatabaseConnectionError("Unexpected server error", extra={"error": str(e)})
