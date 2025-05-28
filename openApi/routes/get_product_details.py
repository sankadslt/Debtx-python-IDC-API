from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from utils.exceptions_handler.custom_exception_handle import NotFoundError
from datetime import datetime
from utils.logger import SingletonLogger
from utils.connectionMongo import MongoDBConnectionSingleton


router = APIRouter()

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')
db_logger = SingletonLogger.get_logger('dbLogger')

case_details_collection ="Case_details"
incident_collection = "Incident"


def get_product_details(case_id: int):
    
    try:
        with MongoDBConnectionSingleton() as db:
            if db is None:
                db_logger.error("Failed to connect to MongoDB.")
                return False, "Failed to connect to MongoDB."

            db_logger.info(f"Connected to MongoDB database: {db.name}")
            logger.info(f"CPY-1P01 - Case Id Received: {case_id}")

            try:
                logger.info(f"CPY-1P01 - Searching for the incident_id in case: {case_id}")
                T1 = datetime.now()
                existing_case_details = db[case_details_collection].find_one({"case_id": case_id})
                T2 = datetime.now()
                logger.info(f"CPY- - Database case query time: {T2-T1}")

                
                if not existing_case_details:
                    logger.warning(f"CPY-1P01 - No case found for case_id: {case_id}")
                    raise NotFoundError("Case not found.")

                incident_id = existing_case_details.get("incident_id")
                if not incident_id:
                    logger.warning(f"CPY-1P01 - No incident_id found for case: {case_id}")
                    raise NotFoundError("Incident not found for the given case.")
                
                logger.info(f"CPY-1P01 - Incident id found: {incident_id}")

                T3 = datetime.now()
                existing_incident_details = db[incident_collection].find_one({"incident_id": incident_id})
                T4 = datetime.now()
                
                logger.info(f"CPY-1P01 - Database incident query time: {T4-T3}")

                if not existing_incident_details:
                    logger.warning(f"CPY-1P01 - Incident details not found for Incident_Id: {incident_id}")
                    raise NotFoundError("Incident details not found.")

                if "product_details" not in existing_incident_details:
                    logger.warning(f"CPY-1P01 - No product details found for incident_id: {incident_id}")
                    raise NotFoundError("Product details not found in the incident.")

                existing_product_details = existing_incident_details["product_details"]
                logger.info(f"CPY-1P01 - Returning product details")
                logger.info(f"CPY-1P03 - Product details found.")

                return existing_product_details
            
            except Exception as e:
                logger.error(f"CPY-1P01 - Unexpected error: {str(e)}")
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
            
    except Exception as e:
        logger.error(f"CPY-1P01 - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")        