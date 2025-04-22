import logging
from datetime import datetime
from config.database.DB_config import case_details_collection, incident_collection
from utils.database.connectDB import get_db_connection
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError, NotFoundError

logger = logging.getLogger("PRODUCT_MANAGER")
db = get_db_connection()

def get_product_details_from_db(case_id, api_id):
    logger.info(f"{api_id} - Searching for the incident id in case: {case_id}")
    T1 = datetime.now()
    incident_id = (db[case_details_collection].find_one({"case_id": int(case_id)}) or {}).get("incident_id")
    T2 = datetime.now()
    logger.info(f"{api_id} - Database case query time: {T2-T1}")

    if not incident_id:
        logger.warning(f"{api_id} - No incident_id found for case: {case_id}")
        raise NotFoundError("Incident not found for the given case.")
    
    logger.info(f"{api_id} - Incident id found: {incident_id}")
    
    T3 = datetime.now()
    incident_details_db = db[incident_collection].find_one({"incident_id": incident_id})
    T4 = datetime.now()
    logger.info(f"{api_id} - Database incident query time: {T4-T3}")

    if not incident_details_db:
        logger.warning(f"{api_id} - Incident details not found for Incident_Id: {incident_id}")
        raise NotFoundError("Incident details not found.")
    
    logger.info(f"{api_id} - Incident found")
    
    if not "product_details" in incident_details_db:
        # logger.warning(f"{api_id} - No product details found for incident_id: {incident_id}")
        raise NotFoundError("Product details not found in the incident.")

    existing_product_details = incident_details_db["product_details"]

    return existing_product_details