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


from pydantic import BaseModel, Field, validator, model_validator
from utils.logger import SingletonLogger
from typing import List, Literal, Optional,Dict, Union
from datetime import datetime
from utils.validators.dateTimeValidator import human_readable_dateTime_to_datetime

SingletonLogger.configure()
logger = SingletonLogger.get_logger('appLogger')


class ProductDetail(BaseModel):
    product_seq: int = Field(None, description="Sequence number of the product") #Mandatory
    product_status: Literal["OK", "SU", "TX", "PE"] = Field(..., description="Status of the product")  #Mandatory
    customer_ref: str = Field(None, description="Customer reference for the product")  #Mandatory
    product_label: str = Field(None, description="Label of the product") #Mandatory
    effective_dtm: datetime = Field(..., description="Effective date-time") #Mandatory
    equipment_ownership: Optional[str] = Field(None, description="Ownership of the equipment")
    product_id: str = Field(None, description="Unique ID of the product") #Mandatory
    product_name: str = Field(None, description="Name of the product")#Mandatory
    service_address: Optional[str] = Field(None, description="Service address for the product")
    cat: Optional[str] = Field(None, description="Category of the product")
    db_cpe_status: Optional[str] = Field(None, description="Database CPE status")
    received_list_cpe_status: Optional[str] = Field(None, description="Received list CPE status")
    service_type: str = Field(None, description="Type of service")#Mandatory
    region: str = Field(None, description="Region of service")#Mandatory
    province: str = Field(None, description="Province of service")#Mandatory
    last_updated_on: Optional[datetime] = Field(None, description="Last updated timestamp")

    @validator("effective_dtm", pre=True)
    def parse_effective_dtm(cls, value):
        return human_readable_dateTime_to_datetime(value)
    
    @model_validator(mode="before")
    def validate_product_details(cls, values):
        errors=[]

        # Extract fields from the validated dictionary
        customer_ref = values.get('customer_ref')
        product_seq = values.get('product_seq')
        product_status = values.get('product_status')
        effective_dtm = values.get('effective_dtm')
        product_label = values.get('product_label')
        product_id = values.get('product_id')
        product_name = values.get('product_name')
        service_type = values.get('service_type')
        region = values.get('region')
        province = values.get('province')
    
        # Validation logic
        if not customer_ref:
            errors.append("Field 'customer_ref' is required and cannot be empty.")
       
        if product_seq is None:
            errors.append("Field 'product_seq' is required.")

        if product_status not in {"OK", "SU", "PE", "TX"}:
            errors.append("Invalid 'product_status'. Allowed values: OK, SU, PE, TX.")
        
        if effective_dtm is None:
            errors.append("Field 'effective_dtm' must be a valid datetime object.")

        if product_label is None:
            errors.append("Field 'product_label' is required.")
        
        if product_id is None:
            errors.append("Field 'product_id' is required.")
        
        if product_name is None:
            errors.append("Field 'product_name' is required.")
        
        if service_type is None:
            errors.append("Field 'service_type' is required.")
        
        if region is None:
            errors.append("Field 'region' is required.")
        
        if province is None:
            errors.append("Field 'province' is required.")
        
        # If errors are found, log and raise exception
        if errors:
            for error in errors:
                logger.error(error)
            raise ValueError(", ".join(errors))

        logger.info(f"Validation successful for product: {values}")
        return values

    

class ExpectedProductDetails(BaseModel):
    case_id: int = Field(..., description="Case ID")
    account_no: int = Field(None, description="Account Number")
    product_details: List[ProductDetail] = Field(None, description="Array of product details")

    @model_validator(mode="before")
    def validate_expected_product_details(cls,value):
        errors=[]
        case_id=value.get('case_id')
        account_no=value.get('account_no')
        product_details=value.get('product_details')

        if not case_id:
            errors.append("Field 'case_id' is required.")
        
        if not account_no:
            errors.append("Field 'account_no' is required.")
        
        if not product_details:
            errors.append("Field 'product_details' is required.")

        if errors:
            for error in errors:
                logger.error(error)
            raise ValueError(", ".join(errors))
        
        logger.info(f"Validation successful for product: {value}")
        return value