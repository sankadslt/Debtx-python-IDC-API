from datetime import datetime
from fastapi.responses import JSONResponse
import re
from pymongo import MongoClient
from utils.coreUtils import config_values
from utils.logger.loggers import get_logger

logger =get_logger("CasePhaseService")


def get_case_phase_logic(case_status: str):
    """
    Retrieves the case phase from the database based on case_status.
    If end_date is in the past, suggests reviewing the case.
    """
    db_client = None

    try:
        db_client = MongoClient(config_values["mongo_uri"])
        database = db_client[config_values["database_name"]]
        logger.info("Connected to MongoDB database successfully")

        try:
            # Initialize the Case_Phases collection
            case_phase_collection = database["Case_Phases"]

            # Ignore the case sensitivity of the case_status
            case_status_regex = re.compile(f"^{case_status}$", re.IGNORECASE)

            # Find the relevant document from the collection
            case_document = case_phase_collection.find_one({"case_status": case_status_regex})

            if not case_document:
                return JSONResponse(content={"error":"Unknown case status", "case_status": case_status}, status_code=404)

            case_phase = case_document.get("case_phase", "Unknown")
            end_dtm = case_document.get("end_dtm")

            # Check if end_dtm is available and it is not a past date
            if end_dtm:
                try:
                    if end_dtm < datetime.now():
                        return JSONResponse(content={"error": "Case status doesn't exist anymore"}, status_code=200)
                except ValueError:
                    return JSONResponse(content={"error": "Invalid date format in database"}, status_code=500)

            return JSONResponse(content={"case_phase": case_phase}, status_code=200)

        except Exception as e:
            return JSONResponse(content={"error": "Unexpected error", "details": str(e)}, status_code=500)

    except Exception as e:
        logger.exception("Error connecting to MongoDB client.")

    # Close the database connection
    finally:
        if db_client is not None:
            db_client.close()
