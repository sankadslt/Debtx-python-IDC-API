#region-Details_Template
"""
API :  
Name :           Create_Cases_From_Incident   
Description :    
Created By :     Iman Chandrasiri(iman.chandrasiri0810@gmail.com) - API Structure, Dulhan Perera (vicksurap@gmail.com) - API Logic, Anupama Maheepala - API Logic
Created No :

Version: 1.0
Input_parameter :  Incident_ID:int

Input:           *Incident_ID:int , Incident document

Output:           *inserting Case_details document

Operation :         *Read Incident document
                    *Map incident data to case details
                    *Insert case details document into Case_details collection
     
Collections:        *Incident                             -Read
                    *Case_details                         -Write

*/   
"""

"""
    Version:Python 3.12.4
    Dependencies: Library
    Related Files: 
    Purpose: creating cases from incident data
    Version:
        version: 1.0
        Last Modified Date: 2024-05-28
        Modified By: Iman Chandrasiri(iman.chandrasiri0810@gmail.com)
        Changes:     

    Notes:
"""
#endregion-Details_Template

from datetime import datetime
from utils.custom_exceptions.custom_exceptions import BaseCustomException, DocumentNotFoundError , DataInsertError
from utils.config_loader_db import config
from utils.db import db 
from utils.get_next_case_id.get_next_case_id import get_next_case_id
from utils.logger.loggers import SingletonLogger
from utils.caseTemplateLoader.caseTemplateLoader import CaseTemplateLoader

SingletonLogger.configure()

# Define loggers at module level
logger = SingletonLogger.get_logger('dbLogger')

def initialize_case_details():
    """Loads the case template structure from config."""
    return CaseTemplateLoader.load_case_template()

def assign_case_details_values(case_details, incident_data, current_time):
    """Assign values from incident to the case_details template."""
    case_details["incident_id"] = incident_data.get("Incident_Id")
    case_details["account_num"] = incident_data.get("Account_Num", "")
    case_details["customer_ref"] = incident_data.get("Product_Details", [{}])[0].get("Customer_Ref", "CUST-REF-UNKNOWN")
    case_details["created_dtm"] = current_time
    case_details["implemented_dtm"] = current_time
    case_details["area"] = incident_data.get("Product_Details", [{}])[0].get("Province", "Unknown")
    case_details["arrears_band"] = incident_data.get("Arrears_Band", "AB-UNKNOWN")
    case_details["bss_arrears_amount"] = incident_data.get("Arrears", 0.0)
    case_details["current_arrears_amount"] = incident_data.get("Arrears", 0.0)
    case_details["current_arrears_band"] = incident_data.get("current_arrears_band", "Default Band")
    case_details["action_type"] = incident_data.get("Actions", "Recovery")
    case_details["drc_commision_rule"] = incident_data.get("drc_commision_rule", "Unknown")
    case_details["last_payment_date"] = incident_data.get("Last_Actions", {}).get("Payment_Created")
    case_details["case_current_status"] = incident_data.get("Incident_Status", "Open No Agent")
    case_details["filtered_reason"] = incident_data.get("Filtered_Reason", None)
    case_details["ref_products"] = incident_data.get("Product_Details", [])
    case_details["updatedAt"] = current_time

    contacts = []
    for contact in incident_data.get("Contact_Details", []):
        contact_type = contact.get("Contact_Type")
        contact_value = contact.get("Contact")
        if contact_type == "Mob":
            contacts.append({"mob": contact_value, "email": "", "lan": "", "address": ""})
        elif contact_type == "email":
            contacts.append({"mob": "", "email": contact_value, "lan": "", "address": ""})
        elif contact_type == "Land":
            contacts.append({"mob": "", "email": "", "lan": contact_value, "address": ""})
    
    full_address = incident_data.get("Customer_Details", {}).get("Full_Address")
    if full_address:
        if contacts:
            contacts[0]["address"] = full_address
        else:
            contacts.append({"mob": "", "email": "", "lan": "", "address": full_address})
    
    case_details["contact"] = contacts

    # Add status history
    case_status_entry = {
        "case_status": incident_data.get("Incident_Status", "Open No Agent"),
        "status_reason": incident_data.get("Status_Description", "Pending"),
        "created_dtm": incident_data.get("Incident_Status_Dtm"),
        "created_by": incident_data.get("Created_By", "admin"),
        "notified_dtm": current_time,
        "expire_dtm": None
    }
    case_details["case_status"].append(case_status_entry)

    return case_details

def map_incident_to_case_details(incident_data, case_id: int):
    """Full mapping from incident to case details."""
    current_time = datetime.now()
    case_details = initialize_case_details()
    case_details = assign_case_details_values(case_details, incident_data, current_time)
    case_details["case_id"] = case_id
    return case_details

# Final API-callable function
async def create_cases_from_incident_process(Incident_ID: int):
    try:
        logger.debug(f"Starting case creation for Incident_ID: {Incident_ID}")
        
        incident_collection = db["Incident"]
        case_details_collection = db["Case_details"]

        incident_document = await incident_collection.find_one({"Incident_Id": Incident_ID})
        if not incident_document:
            raise DocumentNotFoundError(f"No incident document found with Incident_Id: {Incident_ID}")
        
        # Check for duplicates
        existing_case = await case_details_collection.find_one({"incident_id": Incident_ID})
        if existing_case:
            raise DataInsertError(f"Case already exists for incident_id: {Incident_ID}")

        # Get new case ID
        case_id = await get_next_case_id()

        # Map and insert
        case_details_document = map_incident_to_case_details(incident_document, case_id)
        result = await case_details_collection.insert_one(case_details_document)
        if not result.inserted_id:
            raise DataInsertError("Failed to insert case details into the Case_details collection")
        
        logger.info(f"Case created with case_id={case_id}, MongoDB ID={result.inserted_id}")
        return {"message": "Case created", "case_id": case_id}

    except BaseCustomException as ce:
        logger.error(f"Custom exception occurred: {str(ce)}")
       
    except Exception as e:
        logger.exception(f"Unexpected error during case creation process:{str(e)}")
        
