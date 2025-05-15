"""
API : ESO-1P01
Name : Log External Operation
Description : 
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : case_id
    created_dtm
    case_phase
    monitor_expir_dtm
    last_monitor_dtm
    
        
OP : None
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: Log_External_Operation.py, Log_External_Operation_Class.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2025-03-27
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""
from openApi.models.Log_External_Operation_Class import Case_Monitor_Model
from loggers.loggers import get_logger
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from datetime import datetime
from utils.database.connectDB import get_db_connection
from pydantic import ValidationError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError


router = APIRouter()
logger = get_logger("MONITOR_MANAGER")
db = get_db_connection()

external_source_operational_log_collection ="External_Source_Operational_Log"
case_details_collection = "Case_details"

@router.post("/Log_External_Operation", summary="", description = """
""")
async def log_external_operation(request:Case_Monitor_Model):
    logger.info("ESO-1P01 - Log External Operation - request received")
    start_time = datetime.now()

    try:
        existing_case_details = db[case_details_collection].find_one({"case_id": request.case_id}) 
        
        if not  existing_case_details:
            logger.error(f"ESO-1P01 - Log External Operation - Case ID not found: {request.case_id}")
            raise ValidationError("Case ID not found")
        
        logger.info(f"ESO-1P01 - Log External Operation - Case ID: {request.case_id} - Case ID found")

        log_data = request.model_dump()
        log_data["created_dtm"] = datetime.now()
        
        db[external_source_operational_log_collection].insert_one(log_data)
        logger.info(f"ESO-1P01 - Log External Operation - Case ID: {request.case_id} - Log External Operation completed successfully")
         
        return {"message": "Log External Operation completed successfully"}

    except PyMongoError as pe:
        logger.error(f"ESO-1P01 - Log External Operation - PyMongo error: {pe}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

    except ValidationError as ve:
        logger.error(f"C-1P48 - Log External Operation - validation error: {ve}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))
        
    except Exception as e:
        logger.error(f"C-1P48 - Log External Operation - Unexpected error: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")        

    
    
        

    