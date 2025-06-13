from utils.custom_exceptions.custom_exceptions import DocumentNotFoundError, DataInsertError
from utils.config_loader_db import config
from utils.db import db

def get_incident_document(db, Incident_Id: int):
    incident_collection = db["Incident"]
    incident_document = incident_collection.find_one({"Incident_Id": Incident_Id})
    if not incident_document:
        raise DocumentNotFoundError(f"No incident document found with Incident_ID: {incident_id}")
    return incident_document

def check_existing_case(db, Incident_Id: int):
    case_details_collection = db["Case_details"]
    existing_case = case_details_collection.find_one({"incident_id": Incident_Id})
    if existing_case:
        raise DataInsertError(f"Case already exists for Incident_ID: {Incident_Id}")
