
""" 
    Purpose: This template is used for the DRC Routes.
    Created Date: 2025-01-16
    Created By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
    Last Modified Date: 2024-01-26
    Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)       
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: product_manager.py, product_manager_class.py, dateTimeValidator.py
    Notes:
"""

from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from pymongo.errors import PyMongoError
from loggers.loggers import get_logger
from utils.database.connectDB import get_db_connection
from openApi.models.product_manager_class import ExpectedProductDetails
from datetime import datetime
from utils.exceptions_handler.custom_exception_handle import DatabaseError, NotFoundError

router = APIRouter()
logger = get_logger("PRODUCT_MANAGER")
db = get_db_connection()

case_details_collection ="Case_details"
incident_collection = "Incident"

@router.post('/Change_External_Product_Status',summary="Update External Product Status", 
             description="""
Update the status of product_details in the incident.
### Mandatory Fields: 
    - case_id
    - account_no 
    - product_details: 
        -product_seq
        -product_status( Valid product_status: OK, PE, SU, TX )
        -customer_ref 
        -product_label 
        -effective_dtm(Valid effective_dtm format: MM-DD-YYYY HH24:MM:SS)
        -product_id 
        -product_name 
        -service_type 
        -region 
        -province
                """
                )
async def Change_External_Product_Status(request:ExpectedProductDetails):
    logger.info("INC-1P07 - Searching for case Id")

    start_time = datetime.now()

    try:
        case_id = request.case_id
        account_no = request.account_no
        product_details = request.product_details

        logger.info(f"INC-1P07 - Getting incident details for case_id={case_id} and account_no={account_no}")

        # get case details and get incident_id
        case_query = {"case_id": case_id, "account_no": account_no}
        logger.info(f"INC-1P07 - Fetching case details with query: {case_query}")
        # Retrieve case details from the database using the case_id and account_no.
        T1 = datetime.now()
        case_details = db[case_details_collection].find_one(case_query)
        T2 = datetime.now()
        logger.info(f"INC-1P07 - Database case query time: {T2 - T1}")
        
        if not case_details:
            logger.warning(f"INC-1P07 - Case not found for query: {case_query}")
            raise NotFoundError("Case not found.")

        logger.info(f"INC-1P07 - Found case details")

        # Get incident_id from case detail
        incident_id = case_details.get("incident_id")

        if not incident_id:
            logger.warning(f"INC-1P07 - No incident_id found for case: {case_details}")
            raise NotFoundError("Incident not found for the given case.")

        logger.info(f"INC-1P07 - Getting incident details for Incident_Id: {incident_id}")
        # Retrieve incident details from the database using the Incident_Id.
        T3 = datetime.now()
        existing_incident_details = db[incident_collection].find_one({"incident_id": incident_id})
        T4 = datetime.now()
        logger.info(f"INC-1P07 - Database incident query time: {T4 - T3}")

        if not existing_incident_details:
            logger.warning(f"INC-1P07 - Incident details not found for Incident_Id: {incident_id}")
            raise NotFoundError("Incident details not found.")

        logger.info(f"INC-1P07 - Found incident details")

        if not "product_details" in existing_incident_details:
            logger.warning(f"INC-1P07 - No product details found for incident_id: {incident_id}")
            raise NotFoundError("Product details not found in the incident.")

        existing_product_details = existing_incident_details["product_details"]
        
        # Validate recieved product_details array
        for request_product_details in product_details:
        
            customer_ref = getattr(request_product_details, "customer_ref", None)
            product_seq = getattr(request_product_details, "product_seq", None)
            product_status = getattr(request_product_details, "product_status", None)
            # effective_dtm = getattr(request_product_details, "effective_dtm", None)
            
            # Check if the product already exists in the incident details
            existing_product = next(
                (product_item  
                 for product_item  in existing_product_details 
                 if product_item ["customer_ref"] == customer_ref and product_item ["product_seq"] == product_seq
                ),
                None
            )

            if not existing_product:
                # Product does not exist; create and add a new product entry
                logger.info("INC-1P07 - Product not found.")

                end_time = datetime.now()
                logger.info(f"INC-1P07 - Total time taken: {end_time - start_time}")
                
                return{
                    "message": "Product details not found. Please add the product details first."
                }
                
                
            else:

                # Product already exists; check if the status needs to be updated
                if existing_product["product_status"] != product_status:
                    logger.info(f"INC-1P07 - Product found with a different status. Updating status from '{existing_product['product_status']}' to '{product_status}'.")

                    # Update the product status in the existing product
                    existing_product["product_status"] = product_status

                    try:
                        # Update the database with the modified product details
                        db[incident_collection].update_one(
                            {"incident_id": incident_id, "product_details.customer_ref": customer_ref, "product_details.product_seq": product_seq},
                            {"$set": {"product_details.$.product_status": product_status, 
                                      "product_details.$.last_updated_on": datetime.now()
                                      }}
                        )
                        logger.info("INC-1P07 - Database successfully updated with modified product status.")
                        
                        end_time = datetime.now()
                        logger.info(f"INC-1P07 - Total time taken: {end_time - start_time}")

                        return {
                            "message": "Product status has been successfully updated."
                        }
                    except PyMongoError as db_error:
                        logger.error(f"INC-1P07 - Database error during status update: {str(db_error)}")
                        raise DatabaseError("Failed to update the product status in the database.")
                else:
                    logger.info(f"INC-1P07 - Product already exists with the same status: {existing_product['product_status']}. No updates needed.")
                    
                    end_time = datetime.now()
                    logger.info(f"INC-1P07 - Total time taken: {end_time - start_time}")

                    return {
                        "message": "Product status already exists with the same status."
                    }
                
    except Exception as e:
        logger.error(f"INC-1P07 - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

    
@router.post('/Add_External_Product_Details',summary="Add new Product Details",
             description="""

Add new product details to the incident.

### Mandatory Fields:  
    - case_id  
    - account_no
    - product_details: 
        -product_seq
        -product_status(Valid product_status: OK, PE, SU, TX)
        -customer_ref 
        -product_label 
        -effective_dtm(Valid effective_dtm format: MM-DD-YYYY HH24:MM:SS)
        -equipment_ownership
        -product_id 
        -product_name
        -service_address
        -cat
        -db_cpe_status
        -received_list_cpe_status
        -service_type 
        -region 
        -province
"""
)
async def Add_External_Product_Details(request:ExpectedProductDetails):
    logger.info("INC-1P06 - Searching for case Id")
    start_time = datetime.now()

    try:
        
        case_id = request.case_id
        account_no = request.account_no
        product_details = request.product_details

        logger.info(f"INC-1P06 - Getting incident details for case_id={case_id} and account_no={account_no}")

        # get case details and get incident_id
        case_query = {"case_id": case_id, "account_no": account_no}
        logger.info(f"INC-1P06 - Fetching case details with query: {case_query}")
         # Retrieve case details from the database using the case_id and account_no.
        T1 = datetime.now()
        case_details = db[case_details_collection].find_one(case_query)
        T2 = datetime.now()
        logger.info(f"INC-1P06 - Database case query time: {T2 - T1}")
        
        if not case_details:
            logger.warning(f"INC-1P06 - Case not found for query: {case_query}")
            raise NotFoundError("Case not found.")

        logger.info(f"INC-1P06 - Found case details")

        # Get incident_id from case detail
        incident_id = case_details.get("incident_id")

        if not incident_id:
            logger.warning(f"INC-1P06 - No incident_id found for case: {case_details}")
            raise NotFoundError("Incident not found for the given case.")

        logger.info(f"INC-1P06 - Getting incident details for Incident_Id: {incident_id}")
        # Retrieve incident details from the database using the Incident_Id.
        T3 = datetime.now()
        existing_incident_details = db[incident_collection].find_one({"incident_id": incident_id})
        T4 = datetime.now()
        logger.info(f"INC-1P06 - Database incident query time: {T4 - T3}")

        if not existing_incident_details:
            logger.warning(f"INC-1P06 - Incident details not found for Incident_Id: {incident_id}")
            raise NotFoundError("Incident details not found.")

        logger.info(f"INC-1P06 - Found incident details")

        if not "product_details" in existing_incident_details:
            logger.warning(f"INC-1P06 - No product details found for incident_id: {incident_id}")
            raise NotFoundError("Product details not found in the incident.")

        existing_product_details = existing_incident_details["product_details"]
     
        
        new_product = []
        
        # Validate recieved product_details array
        for request_product_details in product_details:
        
            customer_ref = getattr(request_product_details, "customer_ref", None)
            product_seq = getattr(request_product_details, "product_seq", None)
            
            
            # Check if the product already exists in the incident details
            existing_product = next(
                (product_item  
                 for product_item  in existing_product_details 
                 if product_item ["customer_ref"] == customer_ref and product_item ["product_seq"] == product_seq
                ),
                None
            )

            if not existing_product:
                # Product does not exist; create and add a new product entry
                logger.info("INC-1P06 - Product not found. Adding to new array and updating existing details.")
                
                new_product = (request_product_details).model_dump()
                new_product['last_updated_on'] = datetime.now()
                # Append new product to the existing list
                existing_product_details.append(new_product)

                try:
                    # Update the database with new product details
                    db[incident_collection].update_one(
                        {"incident_id": incident_id},  # Match the specific incident
                        {"$set": {"product_details": existing_product_details}}  # Update the product details
                    )
                    logger.info("INC-1P06 - Database successfully updated with new product details.")

                except PyMongoError as db_error:
                    logger.error(f"INC-1P06 - Database error during update: {str(db_error)}")
                    raise DatabaseError("Failed to update the database with product details.")
                
                end_time = datetime.now()
                logger.info(f"INC-1P06 - Total time taken: {end_time - start_time}")
                        
                
                return {
                    "message": "Product details have been successfully added."}
            
            else:
                logger.info("INC-1P06 - Product already exists. No updates needed.") 
                end_time = datetime.now()
                logger.info(f"INC-1P06 - Total time taken: {end_time - start_time}")
                        
                return {
                    "message": "Product details already exists."}
            
    except Exception as e:
        logger.error(f"INC-1P06 - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
