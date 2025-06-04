from utils.custom_exceptions.custom_exceptions import DocumentNotFoundError, DataInsertError
from utils.config_loader_db import config
from utils.db import db

async def get_incident_document(db, incident_id: int):
    incident_collection = db["Incident"]
    incident_document = await incident_collection.find_one({"Incident_ID": incident_id})
    if not incident_document:
        raise DocumentNotFoundError(f"No incident document found with Incident_ID: {incident_id}")
    return incident_document

async def check_existing_case(db, incident_id: int):
    case_details_collection = db["Case_details"]
    existing_case = await case_details_collection.find_one({"Incident_ID": incident_id})
    if existing_case:
        raise DataInsertError(f"Case already exists for Incident_ID: {incident_id}")
