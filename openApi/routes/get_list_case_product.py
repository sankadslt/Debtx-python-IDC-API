import logging
from fastapi import APIRouter, Body, HTTPException
from http import HTTPStatus
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from openApi.routes.get_product_details import get_product_details
from utils.exceptions_handler.custom_exception_handle import NotFoundError
from datetime import datetime
from utils.logger import SingletonLogger

router = APIRouter()

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')

class ProductFilterRequest(BaseModel):
    case_id: int
    filters: Dict[str, Any] = {}

@router.post('/List_Case_Product_Details', summary="List Case Product Details",
             description= """
This endpoint retrieves product details for a given case_id and applies optional filters.
<br>To retrieve all products related to the given case_id, provide no filters.

### Mandatory Fields: 
    - case_id(int, required)
    - filters (dict, optional)
    
### Filtering Options:
    - product_seq
    - product_status("OK", "SU", "PE", "TX")
    - customer_ref
    - product_label
    - effective_dtm
    - equipment_ownership
    - product_id
    - product_name
    - service_address
    - cat
    - db_cpe_status
    - received_list_cpe_status
    - service_type("Fiber", "Standard", "Premium")
    - region
    - province
    - last_updated_on
    
If *no filters* are provided, the API returns *all products* related to the given case_id. """)

async def List_Case_Product_Details(request: ProductFilterRequest):
    """
    Fetch product details for a given case_id and filter using a dictionary.
    """
    case_id = request.case_id
    filters = request.filters  # Dictionary containing filter parameters

    logger.info(f"CPY-1P01 - Case Id Received: {case_id}")
    start_time = datetime.now()

    try:

        existing_product_details = get_product_details(case_id)
        logger.info(f"CPY-1P01 - Product details retrieved successfully.")

        # Filter product details dynamically based on provided parameters in the dictionary
        matching_product_details = [
            product for product in existing_product_details
            if all(str(product.get(key)) == str(value) for key, value in filters.items() if value is not None)
        ]

        if not matching_product_details:
            logger.warning(f"CPY-1P01 - No matching product details found for given filters: {filters}")
            raise NotFoundError(f"No product details found matching the given filters.")

        logger.info(f"CPY-1P01 - Matching product details found: {matching_product_details}")

        end_time = datetime.now()
        logger.info(f"CPY-1P01 - Total time taken: {end_time - start_time}")

        return {
            "case_id": case_id,
            "product_details": matching_product_details
        }

    except Exception as e:
        logger.error(f"CPY-1P01 - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@router.post('/List_Case_Product_Count', summary="List Case Product Attribute Count",
            description=
            """
This endpoint retrieves the count of occurrences for a specific product attribute within a given case_id.

### Mandatory Fields:  
    - case_id (int, required)
    - attribute (str, required): The product attribute to get the count for.  

### Available Attributes for Counting:
    - product_status
    - service_type

"""
)
async def List_Case_Product_Count(
    case_id: int = Body(..., embed=True), 
    attribute: str = Body(..., embed=True)
):
    start_time = datetime.now()
    logger.info(f"CPY-1P02 - Received case_id: {case_id}, attribute: {attribute}")

    try:
        # Retrieve product details
        existing_product_details = get_product_details(case_id)

        if not existing_product_details:
            logger.warning(f"CPY-1P02 - No product details found for case_id {case_id}")
            raise NotFoundError(f"No product details found for the given case_id '{case_id}'.")

        # Check if attribute exists in at least one product
        attribute_found = any(attribute in product for product in existing_product_details)

        if not attribute_found:
            logger.warning(f"CPY-1P02 - Invalid attribute '{attribute}' provided.")
            raise ValidationError(f"The attribute '{attribute}' does not exist in product details.")

        # Count occurrences of the given attribute
        attribute_counts = {}
        for product in existing_product_details:
            if attribute in product:
                attribute_value = product[attribute]  # Get the actual value
                attribute_counts[attribute_value] = attribute_counts.get(attribute_value, 0) + 1

        logger.info(f"CPY-1P02 - {attribute} counts: {attribute_counts}")

        end_time = datetime.now()
        logger.info(f"CPY-1P02 - Total time taken: {end_time - start_time}")

        return {
            "case_id": case_id,
            "attribute": attribute,
            "counts": attribute_counts
        }

    except ValidationError as ve:
        logger.error(f"CPY-1P02 - Validation error: {str(ve)}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f"CPY-1P02 - Unexpected error: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")